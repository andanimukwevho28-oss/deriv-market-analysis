import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import websockets
import yaml
from deepseek_market_analysis import analyze_candles

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.yaml"
DEFAULT_URI = "wss://api.derivws.com/trading/v1/options/ws/public"
LATEST_OHLC_PATH = BASE_DIR / "latest_ohlc.json"
OHLC_HISTORY_PATH = BASE_DIR / "ohlc_history.json"
STATUS_PATH = BASE_DIR / "feed_status.json"
LATEST = {}
CANDLE_HISTORY = {}


def load_config():
    if not CONFIG_PATH.exists():
        return {"symbols": ["R_100"], "timeframes": {"execution": 60, "macro": 300}}
    with CONFIG_PATH.open(encoding="utf-8") as config_file:
        return yaml.safe_load(config_file) or {}


def feed_settings():
    config = load_config()
    symbols = tuple(config.get("symbols") or ["R_100"])
    timeframes = config.get("timeframes", {})
    granularities = tuple(sorted({int(timeframes.get("execution", 60)), int(timeframes.get("macro", 300))}))
    endpoint = config.get("deriv", {}).get("ws_url") or DEFAULT_URI
    return endpoint, symbols, granularities


def write_json(path, value):
    temporary_path = path.with_suffix(".tmp")
    temporary_path.write_text(json.dumps(value, indent=2), encoding="utf-8")
    os.replace(temporary_path, path)


def update_status(connected, error=None):
    write_json(STATUS_PATH, {
        "connected": connected,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "error": error,
    })


async def subscribe_streams(ws, symbols, granularities):
    for symbol in symbols:
        for granularity in granularities:
            payload = {
                "ticks_history": symbol,
                "style": "candles",
                "granularity": granularity,
                "count": 200,
                "end": "latest",
                "subscribe": 1,
            }
            await ws.send(json.dumps(payload))
            print(f"Subscribed to {symbol} {granularity}s candles", flush=True)


def save_latest_ohlc(symbol, candle, granularity):
    epoch = int(candle["epoch"])
    LATEST[symbol] = {
        "symbol": symbol,
        "time": datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat(),
        "epoch": epoch,
        "granularity": granularity,
        "open": float(candle["open"]),
        "high": float(candle["high"]),
        "low": float(candle["low"]),
        "close": float(candle["close"]),
        "source": "deriv_public_ws",
    }
    temporary_path = LATEST_OHLC_PATH.with_suffix(".tmp")
    temporary_path.write_text(json.dumps(LATEST, indent=2), encoding="utf-8")
    os.replace(temporary_path, LATEST_OHLC_PATH)
    print(json.dumps(LATEST[symbol], separators=(",", ":")), flush=True)


def normalize_candle(candle):
    epoch = int(candle.get("open_time", candle["epoch"]))
    return {
        "epoch": epoch,
        "time": datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat(),
        "open": float(candle["open"]),
        "high": float(candle["high"]),
        "low": float(candle["low"]),
        "close": float(candle["close"]),
    }


def save_candle_history(symbol, granularity, candles):
    history_key = (symbol, granularity)
    history = CANDLE_HISTORY.setdefault(history_key, [])
    previous_epoch = history[-1]["epoch"] if history else None

    for candle in candles:
        normalized = normalize_candle(candle)
        if history and history[-1]["epoch"] == normalized["epoch"]:
            history[-1] = normalized
        elif not history or history[-1]["epoch"] < normalized["epoch"]:
            history.append(normalized)

    del history[:-200]
    latest = history[-1]

    latest_by_symbol = {}
    serialized_history = {}
    for (history_symbol, history_granularity), values in CANDLE_HISTORY.items():
        latest_by_symbol.setdefault(history_symbol, {})[str(history_granularity)] = values[-1]
        serialized_history.setdefault(history_symbol, {})[str(history_granularity)] = values
    write_json(LATEST_OHLC_PATH, latest_by_symbol)
    write_json(OHLC_HISTORY_PATH, serialized_history)
    return history, previous_epoch != latest["epoch"]


async def run_market_analysis(symbol, granularity, candles):
    try:
        result = await asyncio.to_thread(analyze_candles, symbol, granularity, candles)
        if result:
            print(f"AI analysis saved for {symbol} ({granularity}s)", flush=True)
    except Exception as exc:
        print(f"AI analysis error for {symbol}: {type(exc).__name__}: {exc}", flush=True)


async def handle_message(msg, default_granularities):
    if msg.get("error"):
        print("API ERROR:", json.dumps(msg["error"]), flush=True)
        return

    request = msg.get("echo_req", {})
    symbol = request.get("ticks_history")
    if not symbol:
        return
    granularity = int(request.get("granularity") or default_granularities[0])

    candles = msg.get("candles")
    if candles:
        history, is_new_candle = save_candle_history(symbol, granularity, candles)
    elif msg.get("ohlc"):
        history, is_new_candle = save_candle_history(symbol, granularity, [msg["ohlc"]])
    else:
        return

    update_status(True)
    if is_new_candle and os.environ.get("DEEPSEEK_API_KEY") and len(history) > 20:
        closed_candles = history[:-1]
        asyncio.create_task(run_market_analysis(symbol, granularity, closed_candles))


async def main():
    delay = 1
    while True:
        try:
            uri, symbols, granularities = feed_settings()
            async with websockets.connect(
                uri, ping_interval=20, ping_timeout=20, open_timeout=15
            ) as ws:
                delay = 1
                settings = (uri, symbols, granularities)
                print(f"Connected to {uri}", flush=True)
                update_status(True)
                await subscribe_streams(ws, symbols, granularities)
                while True:
                    raw = await asyncio.wait_for(ws.recv(), timeout=60)
                    await handle_message(json.loads(raw), granularities)
                    if feed_settings() != settings:
                        print("Feed settings changed; reconnecting", flush=True)
                        break
        except asyncio.CancelledError:
            update_status(False)
            raise
        except Exception as exc:
            update_status(False, f"{type(exc).__name__}: {exc}")
            print(f"Connection error: {type(exc).__name__}: {exc}", flush=True)
            await asyncio.sleep(delay)
            delay = min(delay * 2, 30)


if __name__ == "__main__":
    asyncio.run(main())
