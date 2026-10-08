import streamlit as st

PALETTE = {
    "bg":       "#0e1117",
    "panel":    "#161b22",
    "border":   "#30363d",
    "text":     "#e6edf3",
    "muted":    "#8b949e",
    "green":    "#3fb950",
    "red":      "#f85149",
    "amber":    "#d29922",
    "blue":     "#58a6ff",
    "purple":   "#bc8cff",
}

def apply_theme():
    st.markdown(f"""
    <style>
      .stApp {{ background-color: {PALETTE['bg']}; color: {PALETTE['text']}; }}
      section[data-testid="stSidebar"] {{ background-color: {PALETTE['panel']}; }}
      .block-container {{ padding-top: 2rem; padding-bottom: 2rem; }}
      div[data-testid="stMetricValue"] {{ color: {PALETTE['text']}; }}
      .signal-card {{
        background: {PALETTE['panel']};
        border: 1px solid {PALETTE['border']};
        border-left: 4px solid {PALETTE['blue']};
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
      }}
      .signal-card.buy {{ border-left-color: {PALETTE['green']}; }}
      .signal-card.sell {{ border-left-color: {PALETTE['red']}; }}
      .grade-A {{ color: {PALETTE['green']}; font-weight: 700; }}
      .grade-B {{ color: {PALETTE['blue']}; font-weight: 700; }}
      .grade-C {{ color: {PALETTE['amber']}; font-weight: 700; }}
      .pill {{
        display: inline-block; padding: 2px 10px; border-radius: 12px;
        font-size: 12px; font-weight: 600; margin-right: 6px;
      }}
      .pill.green {{ background: rgba(63,185,80,0.15); color: {PALETTE['green']}; }}
      .pill.red   {{ background: rgba(248,81,73,0.15);  color: {PALETTE['red']}; }}
      .pill.grey  {{ background: rgba(139,148,158,0.15); color: {PALETTE['muted']}; }}
      .status-dot {{
        display: inline-block; width: 8px; height: 8px; border-radius: 50%;
        margin-right: 6px; vertical-align: middle;
      }}
      .status-dot.on  {{ background: {PALETTE['green']}; box-shadow: 0 0 6px {PALETTE['green']}; }}
      .status-dot.off {{ background: {PALETTE['red']}; }}
      .status-dot.wait{{ background: {PALETTE['amber']}; }}
    </style>
    """, unsafe_allow_html=True)