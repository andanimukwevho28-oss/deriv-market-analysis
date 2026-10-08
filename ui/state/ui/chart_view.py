import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render(df: pd.DataFrame, signals: list, symbol: str):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df['time'], open=df['open'], high=df['high'],
        low=df['low'], close=df['close'], name=symbol,
        increasing_line_color="#3fb950", decreasing_line_color="#f85149",
    ))
    for ema, color in (('ema_red','#f85149'), ('ema_green','#3fb950'),
                       ('ema_blue','#58a6ff'), ('ema_brown','#bc8cff')):
        if ema in df.columns:
            fig.add_trace(go.Scatter(
                x=df['time'], y=df[ema], name=ema.replace('ema_','').upper(),
                line=dict(color=color, width=1.4),
            ))

    for s in signals:
        g = s.get('grade', {})
        d = g.get('direction')
        p = s.get('pluto') or s.get('khan') or {}
        if not p.get('entry'): continue
        fig.add_trace(go.Scatter(
            x=[df['time'].iloc[-1]], y=[p['entry']], mode='markers',
            marker=dict(symbol='triangle-up' if d=='BUY' else 'triangle-down',
                        size=16, color='#3fb950' if d=='BUY' else '#f85149'),
            name=f"{d} {g.get('grade')}", showlegend=False,
        ))

    fig.update_layout(
        template="plotly_dark", height=620,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_rangeslider_visible=False,
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
    )
    st.plotly_chart(fig, use_container_width=True)