from typing import Any


def calculate_sustain_tps(tps: float, minutes: float) -> dict[str, Any]:
    """Given TPS and duration in minutes, return total transactions."""
    transactions = tps * 60 * minutes
    explanation = (
        f"{_fmt(tps)} TPS × 60 sec × {_fmt(minutes)} min = "
        f"{_fmt(transactions, 0)} transactions"
    )
    return {
        "transactions": transactions,
        "formula": "transactions = tps × 60 × minutes",
        "explanation": explanation,
        "inputs": {"tps": tps, "minutes": minutes},
    }


def calculate_duration(transactions: float, tps: float) -> dict[str, Any]:
    """Given total transactions and TPS, return duration in seconds and minutes."""
    seconds = transactions / tps
    minutes = seconds / 60
    explanation = (
        f"{_fmt(transactions, 0)} transactions ÷ {_fmt(tps)} TPS = "
        f"{_fmt(seconds)} sec ({_fmt(minutes)} min)"
    )
    return {
        "seconds": seconds,
        "minutes": minutes,
        "formula": "seconds = transactions ÷ tps",
        "explanation": explanation,
        "inputs": {"transactions": transactions, "tps": tps},
    }


def _fmt(value: float, decimals: int = 2) -> str:
    if decimals == 0:
        return f"{value:,.0f}"
    return f"{value:,.{decimals}f}"
