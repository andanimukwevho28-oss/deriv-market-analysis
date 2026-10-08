import streamlit as st
import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    "symbols": ["R_100"],
    "timeframes": {"execution": 60, "macro": 300},
    "pluto": {"ema_red": 9, "ema_green": 21, "ema_blue": 50, "ema_brown": 100, "min_trend_score": 2},
    "khan": {"displacement_atr_mult": 1.0, "fvg_min_atr": 0.3},
    "risk": {"risk_per_trade_pct": 1.0, "max_concurrent_trades": 1, "daily_loss_limit_pct": 3.0},
    "deriv": {"app_id": "", "api_token": "", "ws_url": "wss://api.derivws.com/trading/v1/options/ws/public"},
    "telegram": {"bot_token": "", "chat_id": ""},
}

SYMBOL_OPTIONS = ["R_10", "R_25", "R_50", "R_75", "R_100", "1HZ10V", "1HZ25V", "1HZ50V", "1HZ75V", "1HZ100V"]
TIMEFRAME_OPTIONS = {"1 minute": 60, "5 minutes": 300, "15 minutes": 900, "1 hour": 3600, "1 day": 86400}

def render(config_path="config.yaml"):
    st.subheader("Settings")
    st.caption("The live market feed reconnects automatically when saved settings change.")

    path = Path(config_path)
    cfg = DEFAULT_CONFIG.copy()
    if path.exists():
        with path.open(encoding="utf-8") as f:
            saved = yaml.safe_load(f) or {}
        for key, value in saved.items():
            if isinstance(value, dict) and isinstance(cfg.get(key), dict):
                cfg[key].update(value)
            else:
                cfg[key] = value
    cfg.pop("deepseek", None)

    with st.expander("Symbols & Timeframes", expanded=True):
        current_symbols = cfg.get("symbols", ["R_100"])
        symbol_options = list(dict.fromkeys(SYMBOL_OPTIONS + current_symbols))
        cfg["symbols"] = st.multiselect("Symbols", options=symbol_options, default=current_symbols)
        tf = cfg.setdefault("timeframes", {})
        timeframe_values = list(TIMEFRAME_OPTIONS.values())
        execution = int(tf.get("execution", 60))
        macro = int(tf.get("macro", 300))
        cfg["timeframes"]["execution"] = st.selectbox(
            "Analysis timeframe", timeframe_values,
            index=timeframe_values.index(execution) if execution in timeframe_values else 0,
            format_func=lambda seconds: next(name for name, value in TIMEFRAME_OPTIONS.items() if value == seconds),
        )
        cfg["timeframes"]["macro"] = st.selectbox(
            "Macro timeframe", timeframe_values,
            index=timeframe_values.index(macro) if macro in timeframe_values else 1,
            format_func=lambda seconds: next(name for name, value in TIMEFRAME_OPTIONS.items() if value == seconds),
        )

    with st.expander("Pluto FX"):
        p = cfg['pluto']
        p['ema_red'] = st.slider("Red EMA", 3, 50, p['ema_red'])
        p['ema_green'] = st.slider("Green EMA", 5, 100, p['ema_green'])
        p['ema_blue'] = st.slider("Blue EMA", 20, 200, p['ema_blue'])
        p['ema_brown'] = st.slider("Brown EMA", 50, 400, p['ema_brown'])
        p['min_trend_score'] = st.slider("Min trend score", 1, 3, p['min_trend_score'])

    with st.expander("Khan SMC"):
        k = cfg['khan']
        k['displacement_atr_mult'] = st.slider("Displacement ATR mult", 0.5, 3.0,
                                                float(k['displacement_atr_mult']), 0.1)
        k['fvg_min_atr'] = st.slider("FVG min ATR", 0.1, 2.0,
                                      float(k['fvg_min_atr']), 0.1)

    with st.expander("Risk"):
        r = cfg['risk']
        r['risk_per_trade_pct'] = st.number_input("Risk % / trade",
                                                    value=r['risk_per_trade_pct'], step=0.1)
        r['max_concurrent_trades'] = st.number_input("Max concurrent",
                                                       value=r['max_concurrent_trades'])
        r['daily_loss_limit_pct'] = st.number_input("Daily loss limit %",
                                                     value=r['daily_loss_limit_pct'])

    with st.expander("API Keys"):
        cfg['deriv']['app_id'] = st.text_input("Deriv App ID", cfg['deriv']['app_id'])
        cfg['deriv']['api_token'] = st.text_input("Deriv Token", cfg['deriv']['api_token'],
                                                    type="password")
        st.caption("DeepSeek analysis reads DEEPSEEK_API_KEY from the process environment. It is not stored in config.yaml.")
        cfg['telegram']['bot_token'] = st.text_input("Telegram Bot Token",
                                                       cfg['telegram']['bot_token'],
                                                       type="password")
        cfg['telegram']['chat_id'] = st.text_input("Telegram Chat ID",
                                                     cfg['telegram']['chat_id'])

    st.divider()
    if st.button("Save Settings", type="primary", disabled=not cfg["symbols"]):
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(cfg, f)
        st.success("Saved. The live feed will reconnect with these symbols and timeframe.")