import json
import os
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"
ANALYSIS_PATH = Path(__file__).resolve().with_name("market_analysis.json")


def analyze_candles(symbol, granularity, candles):
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key or len(candles) < 20:
        return None

    market_data = {
        "symbol": symbol,
        "timeframe_seconds": granularity,
        "candles": candles[-100:],
    }
    client = OpenAI(base_url=BASE_URL, api_key=api_key, timeout=45, max_retries=2)
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Analyze the supplied OHLC candles for educational market context. "
                    "Do not recommend buying or selling, give entry or exit instructions, "
                    "or imply certainty. Return only JSON with keys summary, bias, "
                    "observations, and risks. bias must be bullish, bearish, or neutral; "
                    "observations and risks must be short string arrays."
                ),
            },
            {"role": "user", "content": json.dumps(market_data, separators=(",", ":"))},
        ],
        temperature=0.2,
        max_tokens=700,
    )

    content = completion.choices[0].message.content or ""
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        start, end = content.find("{"), content.rfind("}")
        try:
            result = json.loads(content[start : end + 1])
        except (json.JSONDecodeError, ValueError):
            result = {"summary": content, "bias": "neutral", "observations": [], "risks": []}

    record = {
        "symbol": symbol,
        "timeframe_seconds": granularity,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "candle_epoch": candles[-1]["epoch"],
        "model": MODEL,
        "summary": str(result.get("summary", "")),
        "bias": str(result.get("bias", "neutral")).lower(),
        "observations": result.get("observations", []),
        "risks": result.get("risks", []),
    }

    try:
        analyses = json.loads(ANALYSIS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        analyses = {}
    analyses.setdefault(symbol, {})[str(granularity)] = record

    temporary_path = ANALYSIS_PATH.with_suffix(".tmp")
    temporary_path.write_text(json.dumps(analyses, indent=2), encoding="utf-8")
    os.replace(temporary_path, ANALYSIS_PATH)
    return record
