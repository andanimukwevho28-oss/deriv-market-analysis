import streamlit as st
from ui.state.app_state import get_state
from ui.state.market_data import read_feed_status
from ui.ui.components import status_dot

def render():
    state = get_state()
    feed_status = read_feed_status()
    state.connected = bool(feed_status.get("connected"))
    cols = st.columns([1,1,1,1,3])
    with cols[0]:
        status_dot(state.connected, "Deriv feed")
    with cols[1]:
        status_dot(state.running, "Engine")
    with cols[2]:
        status_dot(state.last_candle_ts is not None, "Data feed")
    with cols[3]:
        n = len(state.signals)
        status_dot(n > 0, f"{n} signals", warn=(n == 0))
    with cols[4]:
        error = feed_status.get("error") or state.last_error
        if error:
            st.caption(f"⚠ {error[:80]}")