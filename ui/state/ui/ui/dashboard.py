import streamlit as st
from ui.state.app_state import get_state
from ui.state.market_data import read_analyses
from ui.ui.components import signal_card, empty_state

def render():
    state = get_state()
    st.subheader("AI Market Commentary")
    analyses = read_analyses()

    if not analyses:
        st.caption("Waiting for analysis. Set DEEPSEEK_API_KEY in the environment and start the feed.")
    else:
        for symbol, timeframe_reports in sorted(analyses.items()):
            for timeframe, analysis in sorted(timeframe_reports.items()):
                st.markdown(f"**{symbol} · {analysis.get('bias', 'neutral').title()}**")
                st.caption(
                    f"{timeframe}s candles · {analysis.get('model', 'DeepSeek')} · "
                    f"Updated {analysis.get('updated_at', 'unknown')} · informational only"
                )
                st.write(analysis.get("summary") or "No summary returned.")
                observations = analysis.get("observations") or []
                risks = analysis.get("risks") or []
                if observations:
                    st.caption("Observations: " + " · ".join(map(str, observations)))
                if risks:
                    st.caption("Risks: " + " · ".join(map(str, risks)))

    st.divider()
    st.subheader("Live Signals")

    if not state.signals:
        empty_state("No rule-based signals. DeepSeek commentary is informational and does not generate trades.")
        return

    a = [s for s in state.signals if s.get('grade', {}).get('grade') == 'A']
    b = [s for s in state.signals if s.get('grade', {}).get('grade') == 'B']

    c1, c2, c3 = st.columns(3)
    c1.metric("Grade A", len(a))
    c2.metric("Grade B", len(b))
    c3.metric("Total", len(state.signals))

    st.divider()
    tab_a, tab_b, tab_all = st.tabs(["A-Grade", "B-Grade", "All"])
    with tab_a:
        for s in a[:20]: signal_card(s)
        if not a: empty_state("No A-grade signals.")
    with tab_b:
        for s in b[:20]: signal_card(s)
        if not b: empty_state("No B-grade signals.")
    with tab_all:
        for s in state.signals[:50]: signal_card(s)