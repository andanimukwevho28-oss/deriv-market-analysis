import streamlit as st
import pandas as pd
from ui.state.app_state import get_state

def render():
    state = get_state()
    st.subheader("Signal History")

    if not state.signals:
        st.info("No signals recorded yet.")
        return

    rows = []
    for s in state.signals:
        g = s.get('grade', {})
        p = s.get('pluto') or s.get('khan') or {}
        rows.append({
            "Time": s.get('received_at'),
            "Symbol": s.get('symbol'),
            "Grade": g.get('grade'),
            "Direction": g.get('direction'),
            "Module": p.get('module'),
            "Entry": p.get('entry'),
            "SL": p.get('stop_loss'),
            "TP": p.get('take_profit_1'),
        })
    df = pd.DataFrame(rows)

    c1, c2, c3 = st.columns(3)
    grade_f = c1.multiselect("Grade", ["A","B","C"], default=["A","B"])
    dir_f = c2.multiselect("Direction", ["BUY","SELL"], default=["BUY","SELL"])
    sym_f = c3.multiselect("Symbol", sorted(df['Symbol'].dropna().unique()))

    f = df[df['Grade'].isin(grade_f) & df['Direction'].isin(dir_f)]
    if sym_f: f = f[f['Symbol'].isin(sym_f)]

    st.dataframe(f, use_container_width=True, hide_index=True)

    st.download_button("Export CSV", f.to_csv(index=False), "signals.csv", "text/csv")