import streamlit as st
import plotly.graph_objects as go
from config import CARD, CARD_L, MUTED, WHITE, GRID, BORDER, ANGOLA


PLOTLY_BASE = dict(
    paper_bgcolor=CARD,
    plot_bgcolor=CARD,
    font=dict(color=MUTED, size=11, family="Inter, sans-serif"),
    margin=dict(l=12, r=12, t=44, b=12),
    xaxis=dict(gridcolor=GRID, linecolor=BORDER, zeroline=False),
    yaxis=dict(gridcolor=GRID, linecolor=BORDER, zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED, size=10)),
    hoverlabel=dict(bgcolor="#1A1A2E", font_color=WHITE, font_size=12),
)


def kpi(label, value, sub=None, color="white"):
    cls = {"green":"kpi-pos","red":"kpi-neg","warn":"kpi-warn"}.get(color,"kpi-value")
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div class="kpi">
        <div class="kpi-label">{label}</div>
        <div class="{cls}">{value}</div>
        {sub_html}
    </div>""", unsafe_allow_html=True)


def insight(text, kind="default"):
    cls = {"angola":"insight angola","warn":"insight warn"}.get(kind,"insight")
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)


def section(title, badge=None):
    badge_html = f'<span class="sec-badge">{badge}</span>' if badge else ""
    st.markdown(f"""
    <div class="sec">
        <div class="sec-line"></div>
        <div class="sec-text">{title}</div>
        {badge_html}
    </div>""", unsafe_allow_html=True)


def fig_base(title="", height=380):
    layout = {**PLOTLY_BASE, "height": height}
    if title:
        layout["title"] = dict(text=title, font=dict(color=WHITE, size=13, weight=600), x=0, pad=dict(l=4))
    fig = go.Figure()
    fig.update_layout(**layout)
    return fig


def add_vline(fig, x, label, color=MUTED):
    fig.add_vline(x=x, line_dash="dot", line_color=color, line_width=1)
    fig.add_annotation(
        x=x, yref="paper", y=1.03, text=label, showarrow=False,
        font=dict(size=9, color=color), textangle=-25, xanchor="left",
    )


def add_era_highlight(fig, filtro_era, s):
    if filtro_era == "Todas":
        return
    anos_ord = sorted(int(a) for a in s["Ano"].unique())
    anos_era = [int(a) for a in s[s["Era_Económica"] == filtro_era]["Ano"].unique()]
    if not anos_era:
        return
    ano = anos_era[0]
    if ano not in anos_ord:
        return
    idx = anos_ord.index(ano)
    x0  = ano - 0.4
    x1  = anos_ord[idx + 1] - 0.6 if idx + 1 < len(anos_ord) else ano + 0.4
    fig.add_vrect(x0=x0, x1=x1, fillcolor=ANGOLA, opacity=0.08, layer="below", line_width=0)
    fig.add_annotation(
        x=(x0 + x1) / 2, yref="paper", y=1.07,
        text=filtro_era, showarrow=False,
        font=dict(size=9, color=ANGOLA, weight=600), xanchor="center",
    )
