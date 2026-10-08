import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read_json(filename, default=None):
    path = ROOT / filename
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def read_candles(symbol, granularity):
    history = read_json("ohlc_history.json", {})
    return history.get(symbol, {}).get(str(granularity), [])


def read_analyses():
    return read_json("market_analysis.json", {})


def read_feed_status():
    return read_json("feed_status.json", {"connected": False, "error": None})
