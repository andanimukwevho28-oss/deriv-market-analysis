import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yaml
from pathlib import Path

from ui.theme import apply_theme
from ui.state.ui.ui import dashboard
from ui.state.ui import chart_view, status_bar
from ui.ui import signals_view
from ui.ui.ui import settings_view
from ui.state.app_state import get_state, log
from ui.state.engine_controller import is_running, start, stop
from ui.state.market_data import read_candles, read_feed_status

st.set_page_config(page_title="Pluto × Khan Engine", page_icon="📈", layout="wide")
apply_theme()

state = get_state()
feed_status = read_feed_status()
state.connected = bool(feed_status.get("connected"))
state.running = is_running()

# Sidebar
with st.sidebar:
    st.markdown("### Pluto × Khan")
    st.caption("SMC + EMA Gravity Engine")
    st.divider()
    page = st.radio("Navigate", ["Dashboard", "Chart", "Signals", "Settings", "Log"],
                    label_visibility="collapsed")
    st.divider()
    if st.button("▶ Start Feed" if not state.running else "■ Stop Feed",
                 use_container_width=True, type="primary"):
        if state.running:
            stop()
            state.running = False
            log(state, "Market feed stopped")
        else:
            started = start()
            state.running = is_running()
            log(state, "Market feed started" if started else "Market feed already running")
        st.rerun()
    st.divider()
    st.caption(f"Symbols: {len(st.session_state.get('symbols', []) or [])}")
    st.caption("v0.1.0")

# Status bar
status_bar.render()
st.divider()

# Auto refresh only on Dashboard
if page == "Dashboard":
    st_autorefresh(interval=5000, key="dash_refresh")

# Routes
if page == "Dashboard":
    dashboard.render()
elif page == "Chart":
    st.subheader("Chart")
    try:
        with (Path(__file__).resolve().parents[3] / "config.yaml").open(encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file) or {}
    except OSError:
        config = {"symbols": ["R_100"], "timeframes": {"execution": 60}}
    symbols = config.get("symbols") or ["R_100"]
    timeframes = config.get("timeframes", {})
    granularities = sorted({int(timeframes.get("execution", 60)), int(timeframes.get("macro", 300))})
    c1, c2 = st.columns(2)
    symbol = c1.selectbox("Symbol", symbols)
    granularity = c2.selectbox("Timeframe", granularities, format_func=lambda value: f"{value // 60} min" if value % 60 == 0 else f"{value}s")
    candles = read_candles(symbol, granularity)
    if candles:
        import pandas as pd
        frame = pd.DataFrame(candles)
        frame["time"] = pd.to_datetime(frame["time"], utc=True)
        for key, span in (("ema_red", "ema_red"), ("ema_green", "ema_green"), ("ema_blue", "ema_blue"), ("ema_brown", "ema_brown")):
            period = int(config.get("pluto", {}).get(key, {"ema_red": 9, "ema_green": 21, "ema_blue": 50, "ema_brown": 100}[key]))
            frame[span] = frame["close"].ewm(span=period, adjust=False).mean()
        chart_view.render(frame, [], symbol)
    else:
        st.info("No candles stored for this selection yet. Start the feed to load market data.")
elif page == "Signals":
    signals_view.render()
elif page == "Settings":
    settings_view.render()
elif page == "Log":
    st.subheader("Engine Log")
    if not state.log:
        st.info("No log entries yet.")
    else:
        st.code("\n".join(reversed(state.log)), language="text")

