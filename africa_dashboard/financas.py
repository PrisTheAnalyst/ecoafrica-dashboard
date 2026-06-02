import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from components import kpi, insight, section, fig_base, add_vline, chart_height
from config import (ANGOLA, BLUE, BLUE_L, GREEN, GREEN_L, RED, GOLD,
                    WHITE, MUTED, MUTED_L, BG, CARD, CARD_L, GRID, BORDER)

LIMIAR_DIVIDA_ALTO  = 100
LIMIAR_DIVIDA_MED   = 60
LIMIAR_INF_ALTO     = 20
LIMIAR_INF_MED      = 10


def _empty_state(msg="Sem dados para os filtros seleccionados."):
    st.markdown(
        f'<div style="padding:2rem;text-align:center;color:{MUTED};'
        f'background:#0F0F1A;border:1px dashed #1E1E32;border-radius:12px;'
        f'margin:1rem 0">{msg}</div>',
        unsafe_allow_html=True,
    )


def _cor_divida(v):
    if pd.isna(v):                        return MUTED
    if v >= LIMIAR_DIVIDA_ALTO:           return RED
    if v >= LIMIAR_DIVIDA_MED:            return GOLD
    return GREEN


def _cor_inflacao(v):
    if pd.isna(v):                        return MUTED
    if v >= LIMIAR_INF_ALTO:              return RED
    if v >= LIMIAR_INF_MED:               return GOLD
    return GREEN


def render(p, s, r, m):
    st.markdown('<div class="page-title">Finanças Públicas & Vulnerabilidade</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-desc">Dívida pública, inflação, investimento directo estrangeiro e '
        'scores de vulnerabilidade macroeconómica: 30 países africanos · 2022.</div>',
        unsafe_allow_html=True,
    )

    # ── Filtros ───────────────────────────────────────────────────────────────
    with st.expander("Filtros", expanded=True):
        ff1, ff2, ff3 = st.columns(3)
        with ff1:
            st.markdown('<div class="filter-label">Região</div>', unsafe_allow_html=True)
            reg_opts   = ["Todas"] + sorted(p["Região"].dropna().unique().tolist())
            filtro_reg = st.selectbox("Região", reg_opts, label_visibility="collapsed", key="fin_reg")
        with ff2:
            st.markdown('<div class="filter-label">Grupo de Renda</div>', unsafe_allow_html=True)
            renda_opts   = ["Todos"] + sorted(p["Grupo_Renda_Banco_Mundial"].dropna().unique().tolist())
            filtro_renda = st.selectbox("Renda", renda_opts, label_visibility="collapsed", key="fin_renda")
        with ff3:
            st.markdown('<div class="filter-label">Risco de Dívida</div>', unsafe_allow_html=True)
            risco_opts   = ["Todos", "Alto (≥100% PIB)", "Moderado (60–100%)", "Controlado (<60%)"]
            filtro_risco = st.selectbox("Risco", risco_opts, label_visibility="collapsed", key="fin_risco")

    pf = m["p"].copy()
    if filtro_reg   != "Todas": pf = pf[pf["Região"]                    == filtro_reg]
    if filtro_renda != "Todos": pf = pf[pf["Grupo_Renda_Banco_Mundial"] == filtro_renda]
    if filtro_risco == "Alto (≥100% PIB)":
        pf = pf[pf["Dívida_Pública_%_PIB_2022"] >= LIMIAR_DIVIDA_ALTO]
    elif filtro_risco == "Moderado (60–100%)":
        pf = pf[(pf["Dívida_Pública_%_PIB_2022"] >= LIMIAR_DIVIDA_MED) &
                (pf["Dívida_Pública_%_PIB_2022"] < LIMIAR_DIVIDA_ALTO)]
    elif filtro_risco == "Controlado (<60%)":
        pf = pf[pf["Dívida_Pública_%_PIB_2022"] < LIMIAR_DIVIDA_MED]

    if pf.empty:
        section("Indicadores Fiscais", badge="0 países")
        _empty_state("Nenhum país corresponde à combinação de filtros. Ajuste os critérios.")
        return

    # ── KPIs ─────────────────────────────────────────────────────────────────
    section("Indicadores Fiscais", badge=f"{len(pf)} países")

    div_media  = pf["Dívida_Pública_%_PIB_2022"].mean()
    inf_media  = pf["Inflação_2022_%"].mean()
    ide_total  = pf["IDE_Entrada_2022_USD_Bilhões"].sum()
    n_alto_ris = (pf["Dívida_Pública_%_PIB_2022"] >= LIMIAR_DIVIDA_ALTO).sum()
    ago_div    = m["ago"]["Dívida_Pública_%_PIB_2022"]
    ago_inf    = m["ago"]["Inflação_2022_%"]

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi("Dívida Média",      f"{div_media:.1f}% PIB",  f"limiar risco: {LIMIAR_DIVIDA_MED}%")
    with c2: kpi("Inflação Média",    f"{inf_media:.1f}%",       "preços em 2022",
                 "red" if inf_media >= LIMIAR_INF_ALTO else "warn" if inf_media >= LIMIAR_INF_MED else "green")
    with c3: kpi("IDE Total (grupo)", f"${ide_total:.1f}B",      "investimento estrangeiro 2022")
    with c4: kpi("Risco Fiscal Alto", f"{n_alto_ris} países",   f"dívida ≥ {LIMIAR_DIVIDA_ALTO}% do PIB",
                 "red" if n_alto_ris > 0 else "green")
    with c5: kpi("Angola — Dívida",   f"{ago_div:.1f}% PIB",    f"inflação {ago_inf:.1f}%",
                 "red" if ago_div >= LIMIAR_DIVIDA_ALTO else "warn" if ago_div >= LIMIAR_DIVIDA_MED else "green")

    st.markdown("<div style='margin:.6rem 0'></div>", unsafe_allow_html=True)

    # ── Gráfico A — Dívida pública ranking (bar horizontal) ──────────────────
    section("Dívida Pública: Ranking (% do PIB, 2022)", badge="limiar FMI 60%")

    df_div = pf.dropna(subset=["Dívida_Pública_%_PIB_2022"]).sort_values(
        "Dívida_Pública_%_PIB_2022", ascending=True
    )

    if df_div.empty:
        _empty_state("Sem dados de dívida para o grupo filtrado.")
    else:
        top_div = df_div.nlargest(1, "Dívida_Pública_%_PIB_2022")
        bot_div = df_div.nsmallest(1, "Dívida_Pública_%_PIB_2022")
        insight(
            f"<strong>{top_div.iloc[0]['País']}</strong> tem a maior dívida: "
            f"<strong>{top_div.iloc[0]['Dívida_Pública_%_PIB_2022']:.1f}%</strong> do PIB. "
            f"<strong>{bot_div.iloc[0]['País']}</strong> é o mais sustentável com "
            f"{bot_div.iloc[0]['Dívida_Pública_%_PIB_2022']:.1f}%. "
            f"Angola situa-se em <strong>{ago_div:.1f}%</strong> do PIB."
        )

        cores_div = [
            ANGOLA if row["Código_ISO3"] == "AGO"
            else RED   if row["Dívida_Pública_%_PIB_2022"] >= LIMIAR_DIVIDA_ALTO
            else GOLD  if row["Dívida_Pública_%_PIB_2022"] >= LIMIAR_DIVIDA_MED
            else GREEN
            for _, row in df_div.iterrows()
        ]
        fig_a = fig_base(kind="bar_h", n_items=len(df_div))
        fig_a.add_trace(go.Bar(
            x=df_div["Dívida_Pública_%_PIB_2022"],
            y=df_div["País"],
            orientation="h",
            marker=dict(color=cores_div, line=dict(width=0)),
            text=df_div["Dívida_Pública_%_PIB_2022"].apply(lambda v: f"{v:.0f}%"),
            textposition="outside",
            textfont=dict(color=WHITE, size=9, family="JetBrains Mono"),
            hovertemplate="<b>%{y}</b><br>Dívida: %{x:.1f}% do PIB<extra></extra>",
        ))
        fig_a.add_vline(x=LIMIAR_DIVIDA_MED,  line_dash="dash", line_color=GOLD, line_width=1,
                        annotation_text="60%  Moderado",    annotation_font_color=GOLD,
                        annotation_position="top right",     annotation_font_size=9)
        fig_a.add_vline(x=LIMIAR_DIVIDA_ALTO, line_dash="dash", line_color=RED,  line_width=1,
                        annotation_text="100%   Alto Risco", annotation_font_color=RED,
                        annotation_position="top right",     annotation_font_size=9)
        fig_a.update_xaxes(title=dict(text="% do PIB", font=dict(color=MUTED, size=10)))
        fig_a.update_yaxes(tickfont=dict(size=10))
        st.plotly_chart(fig_a, use_container_width=True)

    # ── Gráfico B + C ─────────────────────────────────────────────────────────
    col_b, col_c = st.columns(2)

    # ── Gráfico B  Inflação: Lollipop/Dot chart (substitui bar horizontal) 

    with col_b:
        section("Inflação — Ranking (%, 2022)", badge="limiar: 10% / 20%")

        df_inf = pf.dropna(subset=["Inflação_2022_%"]).sort_values(
            "Inflação_2022_%", ascending=True
        )
        if df_inf.empty:
            _empty_state("Sem dados de inflação para o grupo filtrado.")
        else:
            top_inf = df_inf.nlargest(1, "Inflação_2022_%").iloc[0]
            insight(
                f"<strong>{top_inf['País']}</strong> regista a inflação mais elevada: "
                f"<strong>{top_inf['Inflação_2022_%']:.1f}%</strong>. "
                f"Angola tem {ago_inf:.1f}% — "
                f"{'acima' if ago_inf >= LIMIAR_INF_ALTO else 'dentro'} do limiar crítico de {LIMIAR_INF_ALTO}%."
            )

            cores_inf = [
                ANGOLA if row["Código_ISO3"] == "AGO"
                else RED   if row["Inflação_2022_%"] >= LIMIAR_INF_ALTO
                else GOLD  if row["Inflação_2022_%"] >= LIMIAR_INF_MED
                else GREEN
                for _, row in df_inf.iterrows()
            ]

            h_lollipop = chart_height("lollipop", len(df_inf))
            fig_b = fig_base(kind="lollipop", n_items=len(df_inf))

            # Linhas do lollipop (de 0 até o valor)
            for i, (_, row) in enumerate(df_inf.iterrows()):
                cor = (
                    ANGOLA if row["Código_ISO3"] == "AGO"
                    else RED   if row["Inflação_2022_%"] >= LIMIAR_INF_ALTO
                    else GOLD  if row["Inflação_2022_%"] >= LIMIAR_INF_MED
                    else GREEN
                )
                fig_b.add_trace(go.Scatter(
                    x=[0, row["Inflação_2022_%"]],
                    y=[row["País"], row["País"]],
                    mode="lines",
                    line=dict(color=cor, width=2),
                    showlegend=False,
                    hoverinfo="skip",
                ))

            # Pontos do lollipop
            fig_b.add_trace(go.Scatter(
                x=df_inf["Inflação_2022_%"],
                y=df_inf["País"],
                mode="markers+text",
                marker=dict(
                    color=cores_inf,
                    size=10,
                    line=dict(width=1, color=CARD),
                ),
                text=df_inf["Inflação_2022_%"].apply(lambda v: f"{v:.1f}%"),
                textposition="middle right",
                textfont=dict(color=WHITE, size=9, family="JetBrains Mono"),
                hovertemplate="<b>%{y}</b><br>Inflação: %{x:.1f}%<extra></extra>",
                showlegend=False,
            ))

            fig_b.add_vline(x=LIMIAR_INF_MED,  line_dash="dash", line_color=GOLD, line_width=1,
                            annotation_text="10%", annotation_font_color=GOLD,
                            annotation_position="top right", annotation_font_size=9)
            fig_b.add_vline(x=LIMIAR_INF_ALTO, line_dash="dash", line_color=RED,  line_width=1,
                            annotation_text="20%", annotation_font_color=RED,
                            annotation_position="top right", annotation_font_size=9)
            fig_b.update_xaxes(title=dict(text="% (inflação anual)", font=dict(color=MUTED, size=10)))
            fig_b.update_yaxes(tickfont=dict(size=10))
            # Margem direita extra para os labels de texto não ficarem cortados
            fig_b.update_layout(margin=dict(l=12, r=60, t=44, b=12))
            st.plotly_chart(fig_b, use_container_width=True)

    # ── Gráfico C — IDE vs PIBpc (scatter bubble) ─────────────────────────────
    with col_c:
        section("IDE Recebido vs PIBpc: Posicionamento", badge="atractividade vs riqueza")

        df_ide = pf.dropna(subset=["IDE_Entrada_2022_USD_Bilhões"]).copy()
        if df_ide.empty:
            _empty_state("Sem dados de IDE para o grupo filtrado.")
        else:
            top_ide = df_ide.nlargest(1, "IDE_Entrada_2022_USD_Bilhões").iloc[0]
            insight(
                f"<strong>{top_ide['País']}</strong> atraiu o maior IDE: "
                f"<strong>${top_ide['IDE_Entrada_2022_USD_Bilhões']:.1f}B</strong>. "
                f"Angola não reportou IDE em 2022 — possível subnotificação ou saída líquida de capital."
            )
            df_ide["Destaque"] = df_ide["Código_ISO3"].apply(
                lambda x: "Angola" if x == "AGO" else "Outros"
            )
            fig_c = px.scatter(
                df_ide,
                x="IDE_Entrada_2022_USD_Bilhões",
                y="PIB_por_Habitante_2023_USD",
                size="PIB_2023_USD_Bilhões",
                color="Destaque",
                hover_name="País",
                color_discrete_map={"Angola": ANGOLA, "Outros": BLUE},
                labels={
                    "IDE_Entrada_2022_USD_Bilhões": "IDE Entrada 2022 ($B)",
                    "PIB_por_Habitante_2023_USD":   "PIBpc 2023 (USD)",
                },
                size_max=40,
            )
            fig_c.update_layout(
                paper_bgcolor=CARD, plot_bgcolor=CARD,
                height=chart_height("scatter"),
                margin=dict(l=12, r=12, t=12, b=12),
                font=dict(color=MUTED, size=11),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED, size=10)),
                xaxis=dict(gridcolor=GRID, zeroline=False),
                yaxis=dict(gridcolor=GRID, zeroline=False),
                hoverlabel=dict(bgcolor="#1A1A2E", font_color=WHITE),
            )
            st.plotly_chart(fig_c, use_container_width=True)

    # ── Gráfico D — Scatter Dívida × Inflação (mapa de risco) ─────────────────
    section("Mapa de Risco Fiscal — Dívida × Inflação (2022)", badge="quadrantes de vulnerabilidade")

    df_risco = pf.dropna(subset=["Dívida_Pública_%_PIB_2022", "Inflação_2022_%"]).copy()
    if df_risco.empty:
        _empty_state("Sem dados suficientes para o mapa de risco.")
    else:
        def classifica_risco(row):
            d = row["Dívida_Pública_%_PIB_2022"]
            i = row["Inflação_2022_%"]
            if d >= LIMIAR_DIVIDA_ALTO or i >= LIMIAR_INF_ALTO:  return "Alto Risco"
            if d >= LIMIAR_DIVIDA_MED  or i >= LIMIAR_INF_MED:   return "Risco Moderado"
            return "Estável"

        df_risco["Risco"] = df_risco.apply(classifica_risco, axis=1)
        n_alto = (df_risco["Risco"] == "Alto Risco").sum()
        n_mod  = (df_risco["Risco"] == "Risco Moderado").sum()
        n_est  = (df_risco["Risco"] == "Estável").sum()
        ago_risco = df_risco[df_risco["Código_ISO3"] == "AGO"]["Risco"].values

        insight(
            f"Do grupo filtrado, <strong>{n_alto}</strong> países em <strong style='color:{RED}'>alto risco</strong>, "
            f"<strong>{n_mod}</strong> em <strong style='color:{GOLD}'>risco moderado</strong> e "
            f"<strong>{n_est}</strong> <strong style='color:{GREEN}'>estáveis</strong>. "
            + (f"Angola está classificada como <strong>{ago_risco[0]}</strong>." if len(ago_risco) > 0 else "")
        )

        cor_map = {"Alto Risco": RED, "Risco Moderado": GOLD, "Estável": GREEN}
        fig_d = px.scatter(
            df_risco,
            x="Dívida_Pública_%_PIB_2022",
            y="Inflação_2022_%",
            size="Populacao_2022_Milhões",
            color="Risco",
            hover_name="País",
            text="País",
            color_discrete_map=cor_map,
            labels={
                "Dívida_Pública_%_PIB_2022": "Dívida Pública (% PIB)",
                "Inflação_2022_%":           "Inflação (%)",
            },
            size_max=45,
        )
        ago_row = df_risco[df_risco["Código_ISO3"] == "AGO"]
        if not ago_row.empty:
            fig_d.add_annotation(
                x=ago_row.iloc[0]["Dívida_Pública_%_PIB_2022"] + 3,
                y=ago_row.iloc[0]["Inflação_2022_%"],
                text="Angola", showarrow=True, arrowhead=2,
                arrowcolor=ANGOLA, arrowsize=0.8, arrowwidth=1.5,
                font=dict(color=ANGOLA, size=11, weight=700), ax=40, ay=-20,
            )
        fig_d.add_vline(x=LIMIAR_DIVIDA_MED,  line_dash="dash", line_color=GOLD, line_width=1,
                        annotation_text="Dívida 60%",   annotation_font_color=GOLD,
                        annotation_font_size=9, annotation_position="top left")
        fig_d.add_vline(x=LIMIAR_DIVIDA_ALTO, line_dash="dash", line_color=RED,  line_width=1,
                        annotation_text="Dívida 100%",  annotation_font_color=RED,
                        annotation_font_size=9, annotation_position="top left")
        fig_d.add_hline(y=LIMIAR_INF_MED,     line_dash="dash", line_color=GOLD, line_width=1,
                        annotation_text="Inflação 10%", annotation_font_color=GOLD,
                        annotation_font_size=9, annotation_position="bottom right")
        fig_d.add_hline(y=LIMIAR_INF_ALTO,    line_dash="dash", line_color=RED,  line_width=1,
                        annotation_text="Inflação 20%", annotation_font_color=RED,
                        annotation_font_size=9, annotation_position="bottom right")
        fig_d.update_traces(textposition="top center", textfont=dict(size=8, color=MUTED_L))
        fig_d.update_layout(
            paper_bgcolor=CARD, plot_bgcolor=CARD,
            height=chart_height("scatter"),
            margin=dict(l=12, r=12, t=12, b=12),
            font=dict(color=MUTED, size=11),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED, size=10)),
            xaxis=dict(gridcolor=GRID, zeroline=False),
            yaxis=dict(gridcolor=GRID, zeroline=False),
            hoverlabel=dict(bgcolor="#1A1A2E", font_color=WHITE),
        )
        st.plotly_chart(fig_d, use_container_width=True)

    # ── Tabela resumo fiscal ───────────────────────────────────────────────────
    section("Tabela Fiscal Completa", badge="2022 · ordenado por dívida")

    df_tab = pf[["País", "Região", "Grupo_Renda_Banco_Mundial",
                 "Dívida_Pública_%_PIB_2022", "Inflação_2022_%",
                 "IDE_Entrada_2022_USD_Bilhões", "Score_Vuln"]].copy()
    df_tab = df_tab.sort_values("Dívida_Pública_%_PIB_2022", ascending=False).reset_index(drop=True)
    df_tab.columns = ["País", "Região", "Grupo Renda", "Dívida (% PIB)", "Inflação (%)", "IDE ($B)", "Score Vuln."]

    def estilo_fiscal(row):
        if row["País"] == "Angola":
            return [f"background-color:#180A00;color:{ANGOLA};font-weight:700;"] * len(row)
        return [""] * len(row)

    def estilo_val(df):
        import pandas as _pd
        styles = df.copy().map(lambda _: "")
        for i, row in df.iterrows():
            d   = row["Dívida (% PIB)"]
            inf = row["Inflação (%)"]
            if not _pd.isna(d):
                if d >= LIMIAR_DIVIDA_ALTO:
                    styles.loc[i, "Dívida (% PIB)"] = f"color:{RED};font-weight:600"
                elif d >= LIMIAR_DIVIDA_MED:
                    styles.loc[i, "Dívida (% PIB)"] = f"color:{GOLD};font-weight:600"
                else:
                    styles.loc[i, "Dívida (% PIB)"] = f"color:{GREEN};font-weight:600"
            if not _pd.isna(inf):
                if inf >= LIMIAR_INF_ALTO:
                    styles.loc[i, "Inflação (%)"] = f"color:{RED};font-weight:600"
                elif inf >= LIMIAR_INF_MED:
                    styles.loc[i, "Inflação (%)"] = f"color:{GOLD};font-weight:600"
                else:
                    styles.loc[i, "Inflação (%)"] = f"color:{GREEN};font-weight:600"
        return styles

    styled = (
        df_tab.style
        .apply(estilo_fiscal, axis=1)
        .apply(estilo_val, axis=None)
        .format({
            "Dívida (% PIB)": lambda v: f"{v:.1f}%" if pd.notna(v) else "N/D",
            "Inflação (%)":   lambda v: f"{v:.1f}%" if pd.notna(v) else "N/D",
            "IDE ($B)":       lambda v: f"${v:.1f}B" if pd.notna(v) else "N/D",
            "Score Vuln.":    lambda v: f"{v:.2f}"   if pd.notna(v) else "N/D",
        })
        .set_properties(**{
            "background-color": CARD, "color": WHITE,
            "border-color": BORDER, "font-size": "12px",
        })
        .set_table_styles([{"selector": "th", "props": [
            ("background-color", "#0A0A16"), ("color", MUTED), ("font-size", "10px"),
            ("font-weight", "600"), ("text-transform", "uppercase"),
            ("letter-spacing", ".08em"), ("border-color", BORDER), ("padding", "8px 12px"),
        ]}])
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown(
        f'<div style="color:{MUTED};font-size:10px;margin-top:.6rem">'
        f'Dados: World Bank 2022 · N/D = dado não disponível · '
        f'Score Vuln. = índice composto de inflação e dívida normalizadas pela média do grupo.</div>',
        unsafe_allow_html=True,
    )
