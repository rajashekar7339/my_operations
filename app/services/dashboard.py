from __future__ import annotations

import asyncio
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "apps.yaml"

NA_VALUES = {None, "", "n/a", "N/A", "na", "NA"}


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def is_na(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() in NA_VALUES:
        return True
    return False


def infer_layout(apps: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Build environments + columns from the first app's urls map."""
    if not apps:
        return [], []

    urls = apps[0]["urls"]
    environments: list[dict[str, Any]] = []
    columns: list[dict[str, Any]] = []

    for env_id, entry in urls.items():
        if not isinstance(entry, dict):
            raise ValueError(
                f"urls.{env_id} must be a map of region → URL (or N/A)"
            )
        regions = list(entry.keys())
        environments.append({"id": env_id, "regions": regions})
        for region in regions:
            columns.append(
                {
                    "key": f"{env_id}.{region}",
                    "env": env_id,
                    "region": region,
                    "label": region,
                }
            )

    return environments, columns


def resolve_url(app_urls: dict[str, Any], column: dict[str, Any]) -> Any:
    entry = app_urls.get(column["env"])
    if not isinstance(entry, dict):
        raise ValueError(f"Missing region map for env '{column['env']}'")
    if column["region"] not in entry:
        return "N/A"
    return entry[column["region"]]


def _na_cell() -> dict[str, Any]:
    return {
        "ok": False,
        "status": None,
        "version": None,
        "url": None,
        "na": True,
        "tone": "na",
    }


async def _fetch_cell(
    client: httpx.AsyncClient, url: str, timeout: float
) -> dict[str, Any]:
    try:
        response = await client.get(url, timeout=timeout)
        status = response.status_code
        if status == 200:
            data = response.json()
            version = data.get("version")
            if version is not None:
                return {
                    "ok": True,
                    "status": status,
                    "version": str(version),
                    "url": url,
                }
            return {
                "ok": False,
                "status": status,
                "version": None,
                "error": "Response missing version field",
                "url": url,
            }
        return {
            "ok": False,
            "status": status,
            "version": None,
            "error": f"HTTP {status}",
            "url": url,
        }
    except httpx.TimeoutException:
        return {
            "ok": False,
            "status": None,
            "version": None,
            "error": "Timeout",
            "url": url,
        }
    except httpx.RequestError as exc:
        return {
            "ok": False,
            "status": None,
            "version": None,
            "error": str(exc),
            "url": url,
        }


def _baseline_version(
    column_keys: list[str], cells: dict[str, dict[str, Any]]
) -> str | None:
    healthy = [
        (key, cells[key]["version"])
        for key in column_keys
        if cells.get(key, {}).get("ok") and cells[key].get("version")
    ]
    if not healthy:
        return None

    counts = Counter(version for _, version in healthy)
    max_count = max(counts.values())
    tied = {v for v, c in counts.items() if c == max_count}

    for _, version in healthy:
        if version in tied:
            return version
    return None


def _apply_tones(
    column_keys: list[str], cells: dict[str, dict[str, Any]]
) -> tuple[str | None, bool]:
    baseline = _baseline_version(column_keys, cells)
    has_conflict = False

    for key in column_keys:
        cell = cells[key]
        if cell.get("na"):
            cell["tone"] = "na"
            continue
        if not cell.get("ok"):
            cell["tone"] = "error"
            continue
        if baseline and cell["version"] == baseline:
            cell["tone"] = "match"
        else:
            cell["tone"] = "conflict"
            has_conflict = True

    return baseline, has_conflict


async def fetch_dashboard() -> dict[str, Any]:
    config = load_config()
    apps_config: list[dict[str, Any]] = config["apps"]
    environments, columns = infer_layout(apps_config)
    column_keys = [c["key"] for c in columns]
    timeout = float(config.get("timeout_seconds", 5))

    async with httpx.AsyncClient() as client:
        tasks = []
        task_meta: list[tuple[int, str]] = []
        ready: dict[tuple[int, str], dict[str, Any]] = {}

        for app_idx, app in enumerate(apps_config):
            for column in columns:
                key = column["key"]
                url = resolve_url(app["urls"], column)
                if is_na(url):
                    ready[(app_idx, key)] = _na_cell()
                    continue
                tasks.append(_fetch_cell(client, str(url), timeout))
                task_meta.append((app_idx, key))

        results = await asyncio.gather(*tasks)

    for (app_idx, key), result in zip(task_meta, results):
        ready[(app_idx, key)] = result

    apps_out = []
    for app_idx, app in enumerate(apps_config):
        cells = {key: ready[(app_idx, key)] for key in column_keys}
        baseline, has_conflict = _apply_tones(column_keys, cells)
        apps_out.append(
            {
                "id": app["id"],
                "name": app["name"],
                "baseline_version": baseline,
                "has_conflict": has_conflict,
                "cells": cells,
            }
        )

    return {
        "environments": environments,
        "columns": columns,
        "apps": apps_out,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
