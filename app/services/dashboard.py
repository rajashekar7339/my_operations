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


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


async def _fetch_env(
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
    env_order: list[str], env_results: dict[str, dict[str, Any]]
) -> str | None:
    healthy = [
        (env, env_results[env]["version"])
        for env in env_order
        if env_results.get(env, {}).get("ok") and env_results[env].get("version")
    ]
    if not healthy:
        return None

    counts = Counter(version for _, version in healthy)
    max_count = max(counts.values())
    tied = {v for v, c in counts.items() if c == max_count}

    for env, version in healthy:
        if version in tied:
            return version
    return None


def _apply_tones(
    env_order: list[str], env_results: dict[str, dict[str, Any]]
) -> tuple[str | None, bool]:
    baseline = _baseline_version(env_order, env_results)
    has_conflict = False

    for env in env_order:
        cell = env_results[env]
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
    env_order: list[str] = config["environments"]
    timeout = float(config.get("timeout_seconds", 5))
    apps_config: list[dict[str, Any]] = config["apps"]

    async with httpx.AsyncClient() as client:
        tasks = []
        task_meta: list[tuple[int, str]] = []

        for app_idx, app in enumerate(apps_config):
            for env in env_order:
                url = app["urls"][env]
                tasks.append(_fetch_env(client, url, timeout))
                task_meta.append((app_idx, env))

        results = await asyncio.gather(*tasks)

    app_env_results: dict[int, dict[str, dict[str, Any]]] = {
        i: {} for i in range(len(apps_config))
    }
    for (app_idx, env), result in zip(task_meta, results):
        app_env_results[app_idx][env] = result

    apps_out = []
    for app_idx, app in enumerate(apps_config):
        env_results = app_env_results[app_idx]
        baseline, has_conflict = _apply_tones(env_order, env_results)
        apps_out.append(
            {
                "id": app["id"],
                "name": app["name"],
                "baseline_version": baseline,
                "has_conflict": has_conflict,
                "environments": env_results,
            }
        )

    return {
        "environments": env_order,
        "apps": apps_out,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
