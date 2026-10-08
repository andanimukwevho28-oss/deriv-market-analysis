import streamlit as st
from ui.theme import PALETTE

def status_dot(ok: bool, label: str, warn=False):
    cls = "wait" if warn else ("on" if ok else "off")
    st.markdown(
        f'<span class="status-dot {cls}"></span>'
        f'<span style="color:{PALETTE["muted"]};font-size:13px;">{label}</span>',
        unsafe_allow_html=True,
    )

def signal_card(sig: dict):
    g = sig.get('grade', {})
    grade = g.get('grade', '?')
    direction = g.get('direction', '—')
    cls = 'buy' if direction == 'BUY' else 'sell'
    grade_cls = f"grade-{grade}" if grade in ("A", "B", "C") else ""

    entry  = sig.get('pluto', {}).get('entry') or sig.get('khan', {}).get('entry')
    sl     = sig.get('pluto', {}).get('stop_loss') or sig.get('khan', {}).get('stop_loss')
    tp     = sig.get('pluto', {}).get('take_profit_1') or sig.get('khan', {}).get('take_profit_1')
    module = sig.get('pluto', {}).get('module') or sig.get('khan', {}).get('module')
    explain = g.get('explanation', '')

    st.markdown(f"""
    <div class="signal-card {cls}">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <span style="font-size:18px;font-weight:700;">{sig.get('symbol','?')}</span>
          <span class="pill {'green' if direction=='BUY' else 'red'}">{direction}</span>
          <span class="pill grey">{module or '—'}</span>
        </div>
        <div class="{grade_cls}" style="font-size:20px;">{grade}</div>
      </div>
      <div style="color:{PALETTE['muted']};font-size:13px;margin-top:8px;">
        {g.get('reason','')}
      </div>
      <div style="display:flex;gap:24px;margin-top:12px;font-size:14px;">
        <div><span style="color:{PALETTE['muted']}">Entry</span><br><b>{entry}</b></div>
        <div><span style="color:{PALETTE['muted']}">SL</span><br><b style="color:{PALETTE['red']}">{sl}</b></div>
        <div><span style="color:{PALETTE['muted']}">TP</span><br><b style="color:{PALETTE['green']}">{tp}</b></div>
      </div>
      {f'<div style="margin-top:12px;color:{PALETTE["text"]};font-size:13px;line-height:1.5;">{explain}</div>' if explain else ''}
    </div>
    """, unsafe_allow_html=True)

def empty_state(msg: str):
    st.markdown(f"""
    <div style="text-align:center;padding:48px;color:{PALETTE['muted']};">
      <div style="font-size:40px;margin-bottom:8px;">◇</div>
      <div>{msg}</div>
    </div>
    """, unsafe_allow_html=True)