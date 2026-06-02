import sys
import os
import base64

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import streamlit as st
import plotly.graph_objects as go

from config import CSS, ANGOLA, BLUE, GOLD, WHITE, MUTED, MUTED_L, BG, CARD, CARD_L, BORDER
import _africa     as africa
import _angola     as angola_page
import financas    as financas_page
import dicionario  as dicionario_page
import extras      as extras_page
from data_loader import load, compute_metrics


st.set_page_config(
    page_title="EcoÁfrica · PIB 2000–2023",
    page_icon=os.path.join(BASE_DIR, "assets", "fundo.png"),
    layout="wide",
    initial_sidebar_state="auto",
)
st.markdown(CSS, unsafe_allow_html=True)

p, s, r = load()
m       = compute_metrics(p, s)


def img_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


with st.sidebar:
    st.markdown('<div class="nav-brand">EcoÁfrica</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-version">Analista</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-sub" style="margin-top:8px">PIB · 2000 – 2023</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-label">Navegação</div>', unsafe_allow_html=True)

    pagina = st.radio(
        label="pagina",
        options=["Capa", "África", "Angola", "Finanças", "Dicionário", "Extras"],
        label_visibility="collapsed",
    )

    st.markdown(
        f'<div style="border-top:1px solid {BORDER};margin:.8rem 0 .4rem;'
        f'color:{MUTED};font-size:9px;letter-spacing:.1em;text-transform:uppercase">'
        f'Referência</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"""
    <div class="nav-footer">
        Fonte: World Bank<br>
        30 países africanos<br>
        2000 – 2023<br><br>
        <span style="color:{ANGOLA};font-weight:600">Angola</span> #8 em África<br>
        <span style="color:#4ADE80;font-weight:600">+831%</span> crescimento acumulado<br>
        <span style="color:#F87171;font-weight:600">−39,8%</span> impacto COVID
    </div>
    """, unsafe_allow_html=True)


if pagina == "Capa":
    img = img_b64(os.path.join(BASE_DIR, "assets", "mumuila.png"))

    st.markdown(f"""
    <style>
    .cover-wrap {{
        position:relative; width:100%; border-radius:20px;
        overflow:hidden; margin-bottom:1.5rem;
        box-shadow: 0 24px 80px rgba(0,0,0,.6);
    }}
    .cover-img {{
        width:100%; height:500px; object-fit:cover;
        object-position:center 18%; display:block; filter:brightness(.35);
    }}
    .cover-overlay {{
        position:absolute; inset:0;
        background:linear-gradient(110deg,
            rgba(8,8,16,.97) 30%,
            rgba(8,8,16,.6) 58%,
            rgba(8,8,16,.05) 100%);
    }}
    .cover-content {{
        position:absolute; top:50%; left:5.5%;
        transform:translateY(-50%); max-width:520px;
    }}
    .cover-eyebrow {{
        color:{ANGOLA}; font-size:10px; font-weight:700;
        letter-spacing:.2em; text-transform:uppercase; margin-bottom:14px;
        display:flex; align-items:center; gap:8px;
    }}
    .cover-eyebrow::before {{
        content:''; display:inline-block; width:24px;
        height:2px; background:{ANGOLA};
    }}
    .cover-title {{
        color:{WHITE}; font-size:50px; font-weight:900;
        line-height:.95; margin-bottom:10px; letter-spacing:-.02em;
    }}
    .cover-subtitle {{
        color:{GOLD}; font-size:16px; font-weight:600;
        margin-bottom:18px; letter-spacing:.04em;
    }}
    .cover-line {{ width:40px; height:2px; background:{ANGOLA}; border-radius:2px; margin-bottom:16px; }}
    .cover-desc {{ color:#B0A898; font-size:13px; line-height:1.8; margin-bottom:28px; }}
    .cover-stats {{ display:flex; gap:28px; align-items:flex-end; flex-wrap:wrap; }}
    .cs-val   {{ color:{WHITE}; font-size:24px; font-weight:800; font-variant-numeric:tabular-nums; }}
    .cs-label {{ color:{MUTED}; font-size:9px; letter-spacing:.1em; text-transform:uppercase; margin-top:3px; }}
    .cs-div   {{ width:1px; height:32px; background:#1E1E32; align-self:center; }}
    </style>

    <div class="cover-wrap">
        <img class="cover-img" src="data:image/png;base64,{img}">
        <div class="cover-overlay"></div>
        <div class="cover-content">
            <div class="cover-eyebrow">Análise Económica · 2000 – 2023</div>
            <div class="cover-title">ÁFRICA<br>PIB &amp;<br>CRESCIMENTO</div>
            <div class="cover-subtitle">30 Países · 23 Anos de Dados</div>
            <div class="cover-line"></div>
            <div class="cover-desc">
                Explore a evolução económica do continente africano, o impacto
                das grandes eras económicas e o posicionamento de Angola entre
                as maiores economias de África.
            </div>
            <div class="cover-stats">
                <div>
                    <div class="cs-val">${m['pib23']:,.0f}B</div>
                    <div class="cs-label">PIB Total 2023</div>
                </div>
                <div class="cs-div"></div>
                <div>
                    <div class="cs-val">+{m['cresc_cont']:.0f}%</div>
                    <div class="cs-label">Crescimento</div>
                </div>
                <div class="cs-div"></div>
                <div>
                    <div class="cs-val">#8</div>
                    <div class="cs-label">Angola em África</div>
                </div>
                <div class="cs-div"></div>
                <div>
                    <div class="cs-val">30</div>
                    <div class="cs-label">Países</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    s_tot = s.groupby(["Ano", "Era_Económica", "Ordem_Era"])["PIB_USD_Bilhões"].sum().reset_index().sort_values("Ano")
    s_ago = s[s["Código_ISO3"] == "AGO"].sort_values("Ano")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=s_tot["Ano"], y=s_tot["PIB_USD_Bilhões"],
        mode="lines", name="África (total)",
        line=dict(color=BLUE, width=2.5),
        fill="tozeroy", fillcolor="rgba(58,58,110,0.08)",
        hovertemplate="<b>África %{x}</b><br>$%{y:.0f}B<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=s_ago["Ano"], y=s_ago["PIB_USD_Bilhões"],
        mode="lines+markers", name="Angola",
        line=dict(color=ANGOLA, width=3),
        marker=dict(size=7, color=ANGOLA, symbol="circle"),
        hovertemplate="<b>Angola %{x}</b><br>$%{y:.1f}B<extra></extra>",
    ))
    anos_disp = [int(a) for a in s["Ano"].unique()]
    for ano, label, cor in [(2006, "Boom", GOLD), (2009, "Crise", "#F87171"),
                             (2014, "Africa Rising", "#27AE60"), (2020, "COVID-19", "#F87171")]:
        if ano in anos_disp:
            fig.add_vline(x=ano, line_dash="dot", line_color=cor, line_width=1)
            fig.add_annotation(x=ano, yref="paper", y=1.03, text=label, showarrow=False,
                               font=dict(size=9, color=cor), textangle=-20, xanchor="left")
    fig.update_layout(
        paper_bgcolor=CARD, plot_bgcolor=CARD,
        height=270, margin=dict(l=12, r=12, t=36, b=12),
        font=dict(color=MUTED, size=11),
        title=dict(text="Evolução do PIB: África Total vs Angola (2000–2023)",
                   font=dict(color=WHITE, size=13, weight=600), x=0),
        xaxis=dict(gridcolor="#14142A", zeroline=False, tickmode="array", tickvals=sorted(anos_disp)),
        yaxis=dict(gridcolor="#14142A", zeroline=False,
                   title=dict(text="PIB ($B)", font=dict(color=MUTED, size=10))),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED, size=11)),
        hoverlabel=dict(bgcolor="#1A1A2E", font_color=WHITE),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin:.8rem 0">
        <div style="background:#0F1A0F;border:1px solid #1E321E;border-radius:8px;
                    padding:6px 14px;font-size:11px;color:#B0C8B0">
            <strong style="color:#F5F0E8">Africa</strong> : visão continental
        </div>
        <div style="background:#1A0F00;border:1px solid {ANGOLA}44;border-radius:8px;
                    padding:6px 14px;font-size:11px;color:#C8B890">
            <strong style="color:{ANGOLA}">Angola</strong> : posição e comparação
        </div>
        <div style="background:#0F0F1A;border:1px solid #2A1A6A;border-radius:8px;
                    padding:6px 14px;font-size:11px;color:{MUTED_L}">
            <strong style="color:#F5F0E8">Finanças</strong> : dívida & inflação
        </div>
        <div style="background:#0F0F1A;border:1px solid {BORDER};border-radius:8px;
                    padding:6px 14px;font-size:11px;color:{MUTED_L}">
            <strong style="color:#F5F0E8">Dicionário</strong> : glossário & KPIs
        </div>
        <div style="background:#0F0F1A;border:1px solid {BORDER};border-radius:8px;
                    padding:6px 14px;font-size:11px;color:{MUTED_L}">
            <strong style="color:#F5F0E8">Extras</strong> : changelog & roadmap
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
                padding:.8rem 0;border-top:1px solid {BORDER};margin-top:.5rem">
        <div style="color:{MUTED};font-size:11px">
            Fonte: World Bank &nbsp;·&nbsp; 30 países · 2000–2023
        </div>
        <div style="color:{MUTED};font-size:11px">
            Navegue pelo menu lateral para explorar os dashboards.
        </div>
    </div>
    """, unsafe_allow_html=True)


elif pagina == "África":
    africa.render(p, s, r, m)

elif pagina == "Angola":
    angola_page.render(p, s, r, m)

elif pagina == "Finanças":
    financas_page.render(p, s, r, m)

elif pagina == "Dicionário":
    dicionario_page.render(p, s, r, m)

elif pagina == "Extras":
    extras_page.render(p, s, r, m)
