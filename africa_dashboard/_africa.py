import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from components import kpi, insight, section, fig_base, add_vline, add_era_highlight, chart_height
from config import (ANGOLA, BLUE, BLUE_L, GREEN, GREEN_L, RED, GOLD,
                    WHITE, MUTED, MUTED_L, BG, CARD, CARD_L, GRID, BORDER, CORES_LINHA)


def _empty_state(msg="Nenhum país corresponde aos filtros seleccionados."):
    st.markdown(
        f'<div style="padding:2rem;text-align:center;color:{MUTED};'
        f'background:#0F0F1A;border:1px dashed #1E1E32;border-radius:12px;'
        f'margin:1rem 0">{msg}</div>',
        unsafe_allow_html=True,
    )


def render(p, s, r, m):
    st.markdown('<div class="page-title">Africa Economia 2000–2023</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-desc">PIB de 30 países africanos ao longo de 23 anos · '
        'Crescimento, distribuição regional e posicionamento das maiores economias do continente.</div>',
        unsafe_allow_html=True,
    )

    # ── Filtros ───────────────────────────────────────────────────────────────
    with st.expander("Filtros", expanded=True):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            st.markdown('<div class="filter-label">Região</div>', unsafe_allow_html=True)
            reg_opts   = ["Todas"] + sorted(p["Região"].dropna().unique().tolist())
            filtro_reg = st.selectbox("Região", reg_opts, label_visibility="collapsed", key="af_reg")
        with fc2:
            st.markdown('<div class="filter-label">Perfil Económico</div>', unsafe_allow_html=True)
            perf_opts   = ["Todos"] + sorted(p["Perfil_Económico"].dropna().unique().tolist())
            filtro_perf = st.selectbox("Perfil", perf_opts, label_visibility="collapsed", key="af_perf")
        with fc3:
            st.markdown('<div class="filter-label">Era Económica — destaque no gráfico de linhas</div>', unsafe_allow_html=True)
            eras_df    = s[["Era_Económica", "Ordem_Era"]].drop_duplicates().sort_values("Ordem_Era")
            era_opts   = ["Todas"] + eras_df["Era_Económica"].tolist()
            filtro_era = st.selectbox("Era", era_opts, label_visibility="collapsed", key="af_era")

    pf = p.copy()
    if filtro_reg  != "Todas": pf = pf[pf["Região"]           == filtro_reg]
    if filtro_perf != "Todos": pf = pf[pf["Perfil_Económico"] == filtro_perf]

    if pf.empty:
        section("Indicadores Chave", badge="0 países")
        _empty_state("Nenhum país corresponde à combinação de filtros. Ajuste a Região ou o Perfil Económico.")
        return

    # ── KPIs ─────────────────────────────────────────────────────────────────
    section("Indicadores Chave", badge=f"{len(pf)} países")
    c1, c2, c3, c4, c5 = st.columns(5)

    pib23_f   = pf["PIB_2023_USD_Bilhões"].sum()
    pib00_f   = pf["PIB_2000_USD_Bilhões"].sum()
    cresc_f   = (pib23_f - pib00_f) / pib00_f * 100 if pib00_f else 0
    pibpc_f   = pf["PIB_por_Habitante_2023_USD"].mean()
    acima_f   = int((pf["PIB_por_Habitante_2023_USD"] > pibpc_f).sum())
    maior_c_f = pf.nlargest(1, "Crescimento_Acumulado_2000_2023_%")["País"].values[0]
    max_c_f   = pf["Crescimento_Acumulado_2000_2023_%"].max()

    with c1: kpi("PIB Total 2023",       f"${pib23_f:,.0f}B",   f"era ${pib00_f:,.0f}B em 2000")
    with c2: kpi("Crescimento",          f"+{cresc_f:.0f}%",     "PIB 2000 → 2023", "green")
    with c3: kpi("PIBpc Médio",          f"${pibpc_f:,.0f}",     "por habitante 2023")
    with c4: kpi("Acima da média PIBpc", f"{acima_f} de {len(pf)}", "países com PIBpc > média")
    with c5: kpi("Maior Crescimento",    maior_c_f,              f"+{max_c_f:.0f}% acumulado", "warn")

    st.markdown("<div style='margin:.6rem 0'></div>", unsafe_allow_html=True)

    # ── Gráfico 1 — Mapa ─────────────────────────────────────────────────────
    section("Crescimento Acumulado por País (2000–2023)", badge="crescimento %")

    top3 = pf.nlargest(3, "Crescimento_Acumulado_2000_2023_%")[["País", "Crescimento_Acumulado_2000_2023_%"]]
    bot1 = pf.nsmallest(1, "Crescimento_Acumulado_2000_2023_%")[["País", "Crescimento_Acumulado_2000_2023_%"]]

    top3_txt = " · ".join(
        f"<strong>{row['País']}</strong> +{row['Crescimento_Acumulado_2000_2023_%']:.0f}%"
        for _, row in top3.iterrows()
    ) if not top3.empty else "—"

    menor_crescimento_txt = (
        f"<strong>{bot1.iloc[0]['País']}</strong> +{bot1.iloc[0]['Crescimento_Acumulado_2000_2023_%']:.0f}%."
        if not bot1.empty else "Sem dados disponíveis"
    )

    insight(f"Maiores crescimentos: {top3_txt}. Menor crescimento: {menor_crescimento_txt}")

    fig_map = px.choropleth(
        pf, locations="Código_ISO3",
        color="Crescimento_Acumulado_2000_2023_%",
        hover_name="País",
        hover_data={
            "Crescimento_Acumulado_2000_2023_%": ":.1f",
            "PIB_2023_USD_Bilhões": ":.1f",
            "Código_ISO3": False,
        },
        color_continuous_scale=[[0, RED], [0.3, "#E8720A"], [0.6, GOLD], [1, GREEN]],
        scope="africa",
        labels={
            "Crescimento_Acumulado_2000_2023_%": "Crescimento (%)",
            "PIB_2023_USD_Bilhões": "PIB ($B)",
        },
    )
    fig_map.update_geos(
        bgcolor=BG, showframe=False, showcoastlines=False,
        landcolor="#14142A", oceancolor=BG, showocean=True,
        showcountries=True, countrycolor=BORDER,
    )
    fig_map.update_layout(
        paper_bgcolor=BG, height=chart_height("map"), margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(
            title=dict(text="Crescimento (%)", font=dict(color=MUTED, size=11)),
            tickfont=dict(color=MUTED, size=10), bgcolor=CARD,
            thickness=12, len=0.7,
        ),
        font=dict(color=MUTED),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # ── Gráfico 2 + 4 ────────────────────────────────────────────────────────
    col2, col4 = st.columns(2)

    with col2:
        section("Top 10 Economias PIB 2023", badge="USD bilhões")
        top10 = pf.nlargest(10, "PIB_2023_USD_Bilhões").sort_values("PIB_2023_USD_Bilhões")

        if top10.empty:
            _empty_state("Sem dados para o ranking com os filtros actuais.")
        else:
            maior = top10.iloc[-1]
            angola_rank_vals = pf[pf["Código_ISO3"] == "AGO"]["Ranking_PIB_2023"].values
            angola_rank      = int(angola_rank_vals[0]) if len(angola_rank_vals) > 0 else "N/A"

            if angola_rank != "N/A":
                angola_txt = f"Angola ocupa a posição <strong>#{angola_rank}</strong> no continente."
            else:
                angola_txt = "Angola não está incluída nos filtros actuais."

            insight(
                f"<strong>{maior['País']}</strong> lidera com ${maior['PIB_2023_USD_Bilhões']:.0f}B. "
                f"{angola_txt}",
                "angola",
            )

            cores = [ANGOLA if x == "AGO" else BLUE for x in top10["Código_ISO3"]]
            fig2  = fig_base(kind="bar_h", n_items=len(top10))
            fig2.add_trace(go.Bar(
                x=top10["PIB_2023_USD_Bilhões"], y=top10["País"], orientation="h",
                marker=dict(color=cores, line=dict(width=0)),
                text=top10["PIB_2023_USD_Bilhões"].apply(lambda v: f"${v:.0f}B"),
                textposition="outside", textfont=dict(color=WHITE, size=10, family="JetBrains Mono"),
                hovertemplate="<b>%{y}</b><br>PIB 2023: $%{x:.1f}B<extra></extra>",
            ))
            fig2.update_xaxes(showticklabels=False, showgrid=False)
            fig2.update_yaxes(tickfont=dict(size=11))
            st.plotly_chart(fig2, use_container_width=True)

    with col4:
        section("PIB por Região: 2000, 2010 e 2023", badge="evolução regional")
        r_ord = r.sort_values("PIB_Total_2023_Bi", ascending=False)

        if r_ord.empty:
            _empty_state("Sem dados de regiões disponíveis.")
        else:
            maior_reg     = r_ord.iloc[0]
            mais_cresc_df = r.nlargest(1, "Crescimento_Acumulado_Região_%")
            mais_cresc    = mais_cresc_df.iloc[0] if not mais_cresc_df.empty else None

            if mais_cresc is not None:
                insight(
                    f"<strong>{maior_reg['Região']}</strong> domina com ${maior_reg['PIB_Total_2023_Bi']:.0f}B. "
                    f"Região de maior crescimento acumulado: <strong>{mais_cresc['Região']}</strong> "
                    f"+{mais_cresc['Crescimento_Acumulado_Região_%']:.0f}%."
                )
            else:
                insight(f"<strong>{maior_reg['Região']}</strong> domina com ${maior_reg['PIB_Total_2023_Bi']:.0f}B.")

            fig4 = fig_base(kind="bar_v")
            for ano_col, cor, nome in [
                ("PIB_Total_2000_Bi", "#1E2D6A", "2000"),
                ("PIB_Total_2010_Bi", BLUE,      "2010"),
                ("PIB_Total_2023_Bi", ANGOLA,    "2023"),
            ]:
                fig4.add_trace(go.Bar(
                    name=nome, x=r_ord["Região"], y=r_ord[ano_col],
                    marker=dict(color=cor, line=dict(width=0)),
                    text=r_ord[ano_col].apply(lambda v: f"${v:.0f}B"),
                    textposition="outside", textfont=dict(size=9, color=MUTED_L),
                    hovertemplate=f"<b>%{{x}}</b><br>{nome}: $%{{y:.1f}}B<extra></extra>",
                ))
            fig4.update_layout(barmode="group", bargap=0.2, bargroupgap=0.05)
            fig4.update_yaxes(showticklabels=False)
            st.plotly_chart(fig4, use_container_width=True)

    # ── Gráfico 3 — Linhas ───────────────────────────────────────────────────
    section("Evolução do PIB: 7 Maiores Economias por Era (2000–2023)", badge="série temporal")

    if filtro_era != "Todas":
        insight(
            f"Era em destaque: <strong>{filtro_era}</strong>. "
            "A faixa laranja indica o período seleccionado no gráfico abaixo."
        )

    isos_visiveis = pf["Código_ISO3"].unique()
    sf = s[s["Código_ISO3"].isin(isos_visiveis)]

    if sf.empty:
        _empty_state("Sem dados de série temporal para os países seleccionados.")
    else:
        fig3 = fig_base(kind="line")
        add_era_highlight(fig3, filtro_era, s)

        for iso in sf["Código_ISO3"].unique():
            df_i  = sf[sf["Código_ISO3"] == iso].sort_values("Ano")
            nome  = df_i["País"].iloc[0]
            cor   = CORES_LINHA.get(iso, BLUE)
            width = 3 if iso == "AGO" else 1.5
            fig3.add_trace(go.Scatter(
                x=df_i["Ano"], y=df_i["PIB_USD_Bilhões"],
                mode="lines+markers", name=nome,
                line=dict(color=cor, width=width, dash="solid"),
                marker=dict(size=6 if iso == "AGO" else 4, symbol="circle"),
                hovertemplate=f"<b>{nome} %{{x}}</b><br>PIB: $%{{y:.1f}}B<extra></extra>",
            ))

        anos_disponiveis = sorted(int(a) for a in s["Ano"].unique())
        for ano, label, cor in [
            (2006, "Boom",          GOLD),
            (2009, "Crise",         RED),
            (2014, "Africa Rising", GREEN),
            (2020, "COVID-19",      RED),
        ]:
            if ano in anos_disponiveis:
                add_vline(fig3, ano, label, cor)

        fig3.update_xaxes(tickmode="array", tickvals=anos_disponiveis, tickfont=dict(size=10))
        fig3.update_yaxes(title=dict(text="PIB ($B)", font=dict(color=MUTED, size=10)))
        st.plotly_chart(fig3, use_container_width=True)
