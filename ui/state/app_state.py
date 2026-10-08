import asyncio
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import streamlit as st

@dataclass
class EngineState:
    running: bool = False
    connected: bool = False
    last_candle_ts: Optional[datetime] = None
    last_error: Optional[str] = None
    signals: list = field(default_factory=list)
    log: list = field(default_factory=list)

def get_state() -> EngineState:
    if "engine_state" not in st.session_state:
        st.session_state.engine_state = EngineState()
    return st.session_state.engine_state

def log(state: EngineState, msg: str):
    ts = datetime.utcnow().strftime("%H:%M:%S")
    state.log.append(f"[{ts}] {msg}")
    state.log = state.log[-200:]  # cap

def push_signal(state: EngineState, sig: dict):
    sig['received_at'] = datetime.utcnow()
    state.signals.insert(0, sig)
    state.signals = state.signals[:500]