import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from components import kpi, insight, section, fig_base, add_vline, add_era_highlight
from config import (ANGOLA, ANGOLA_D, BLUE, BLUE_L, GREEN, GREEN_L, RED, GOLD,
                    WHITE, MUTED, MUTED_L, CARD, CARD_L, GRID, BORDER,
                    PEERS, PEERS_N, PEERS_C, TOP5_ISO)


def _empty_state(msg="Sem dados para os filtros seleccionados."):
    st.markdown(
        f'<div style="padding:2rem;text-align:center;color:{MUTED};'
        f'background:#0F0F1A;border:1px dashed #1E1E32;border-radius:12px;'
        f'margin:1rem 0">{msg}</div>',
        unsafe_allow_html=True,
    )


def _badge_filtro(filtro_era, filtro_vuln):
    """Pill informativa activa quando há filtros seleccionados."""
    partes = []
    if filtro_era  != "Todas": partes.append(f"Era: <strong>{filtro_era}</strong>")
    if filtro_vuln != "Todos": partes.append(f"Vuln: <strong>{filtro_vuln}</strong>")
    if not partes:
        return
    st.markdown(
        f'<div style="display:inline-flex;gap:8px;align-items:center;'
        f'background:#1A0F00;border:1px solid {ANGOLA}44;border-radius:8px;'
        f'padding:5px 12px;font-size:11px;color:{MUTED};margin-bottom:.8rem">'
        f'<span style="color:{ANGOLA};font-weight:700">Filtros activos</span>'
        f'&nbsp;·&nbsp;' + "&nbsp;·&nbsp;".join(partes) +
        f'</div>',
        unsafe_allow_html=True,
    )


def render(p, s, r, m):
    ago = m["ago"]

    st.markdown('<div class="page-title">Angola: Posição Continental</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-desc">Angola cresceu +831% desde 2000 quase o triplo da média africana. '
        'O PIBpc cresceu +312%, mas permanece abaixo da média continental. '
        'Crescer muito não é o mesmo que enriquecer por habitante.</div>',
        unsafe_allow_html=True,
    )

    # ── Filtros ───────────────────────────────────────────────────────────────
    with st.expander("Filtros", expanded=True):
        fc1, fc2 = st.columns(2)
        with fc1:
            st.markdown('<div class="filter-label">Era Económica</div>', unsafe_allow_html=True)
            eras_df    = s[["Era_Económica", "Ordem_Era"]].drop_duplicates().sort_values("Ordem_Era")
            era_opts   = ["Todas"] + eras_df["Era_Económica"].tolist()
            filtro_era = st.selectbox("Era", era_opts, label_visibility="collapsed", key="ao_era")
        with fc2:
            st.markdown('<div class="filter-label">Score Vulnerabilidade</div>', unsafe_allow_html=True)
            vuln_opts   = ["Todos", "Abaixo da média (< 1.0)", "Acima da média (≥ 1.0)"]
            filtro_vuln = st.selectbox("Score", vuln_opts, label_visibility="collapsed", key="ao_vuln")

    # ── Derivar conjuntos filtrados ───────────────────────────────────────────
    # pf  → países filtrados por vulnerabilidade (Angola incluída sempre)
    pf = m["p"].copy()
    if filtro_vuln == "Abaixo da média (< 1.0)":
        pf = pf[(pf["Score_Vuln"] < 1.0) | (pf["Código_ISO3"] == "AGO")]
    elif filtro_vuln == "Acima da média (≥ 1.0)":
        pf = pf[(pf["Score_Vuln"] >= 1.0) | (pf["Código_ISO3"] == "AGO")]

    # sf  → série temporal filtrada por era (todos os peers, restrito ao período)
    sf = s.copy()
    anos_era = None
    if filtro_era != "Todas":
        anos_era = sorted(sf[sf["Era_Económica"] == filtro_era]["Ano"].unique())
        sf = sf[sf["Ano"].isin(anos_era)]

    # Métricas do grupo filtrado (usadas nos KPIs e insights)
    grupo_pibpc  = pf["PIB_por_Habitante_2023_USD"].mean()
    grupo_cresc  = pf["Crescimento_Acumulado_2000_2023_%"].mean()
    n_grupo      = len(pf)
    label_grupo  = f"grupo ({n_grupo})" if filtro_vuln != "Todos" else "África (30)"

    # Angola — valores do período filtrado (via sf) ou acumulados
    s_ago = sf[sf["Código_ISO3"] == "AGO"].sort_values("Ano")
    if not s_ago.empty and filtro_era != "Todas":
        pib_ago_inicio = float(s_ago["PIB_USD_Bilhões"].iloc[0])
        pib_ago_fim    = float(s_ago["PIB_USD_Bilhões"].iloc[-1])
        cresc_era_ago  = (pib_ago_fim - pib_ago_inicio) / pib_ago_inicio * 100 if pib_ago_inicio else 0
    else:
        cresc_era_ago  = ago["Crescimento_Acumulado_2000_2023_%"]

    _badge_filtro(filtro_era, filtro_vuln)

    # ── KPIs ─────────────────────────────────────────────────────────────────
    section("Indicadores Chave Angola", badge=label_grupo)

    diff_cresc = cresc_era_ago - grupo_cresc
    diff_pibpc = ago["PIB_por_Habitante_2023_USD"] - grupo_pibpc

    # PIB Angola no período da era (ou 2023 se "Todas")
    pib_ago_display = float(s_ago["PIB_USD_Bilhões"].iloc[-1]) if (not s_ago.empty and filtro_era != "Todas") else ago["PIB_2023_USD_Bilhões"]
    pib_ago_base    = float(s_ago["PIB_USD_Bilhões"].iloc[0])  if (not s_ago.empty and filtro_era != "Todas") else ago["PIB_2000_USD_Bilhões"]
    label_ano_fim   = int(s_ago["Ano"].iloc[-1]) if (not s_ago.empty and filtro_era != "Todas") else 2023
    label_ano_base  = int(s_ago["Ano"].iloc[0])  if (not s_ago.empty and filtro_era != "Todas") else 2000

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi(f"PIB Angola {label_ano_fim}",
                 f"${pib_ago_display:.1f}B",
                 f"era ${pib_ago_base:.1f}B em {label_ano_base}")
    with c2: kpi("Ranking em África",
                 f"#{int(ago['Ranking_PIB_2023'])} de 30",
                 f"#{int(ago['Ranking_PIBpc_2023'])}º em PIBpc")
    with c3: kpi(f"Cresc. vs {label_grupo}",
                 f"{diff_cresc:+.0f}pp",
                 f"+{cresc_era_ago:.0f}% Angola vs média +{grupo_cresc:.0f}%",
                 "green" if diff_cresc >= 0 else "red")
    with c4: kpi(f"PIBpc vs {label_grupo}",
                 f"${diff_pibpc:+,.0f}",
                 f"${ago['PIB_por_Habitante_2023_USD']:,} vs média ${grupo_pibpc:,.0f}",
                 "red" if diff_pibpc < 0 else "green")
    with c5: kpi("Impacto COVID",
                 f"{ago['Impacto_COVID_%']:.1f}%",
                 f"média {label_grupo} {pf['Impacto_COVID_%'].mean():.1f}%", "red")

    st.markdown("<div style='margin:.6rem 0'></div>", unsafe_allow_html=True)

    # ── Gráfico 5 — Linhas peers ──────────────────────────────────────────────
    # Peers: sempre Angola + NGA + ZAF + ETH, mas restritos ao período da era
    peers_no_grupo = [iso for iso in PEERS if iso == "AGO" or iso in pf["Código_ISO3"].values]
    s_peers = sf[sf["Código_ISO3"].isin(peers_no_grupo)].sort_values(["Código_ISO3", "Ano"])

    era_label = f" · Era: {filtro_era}" if filtro_era != "Todas" else ""
    section(f"Angola vs Peers: Evolução PIB{era_label}", badge="NGR · ZAF · ETH")

    if s_peers.empty:
        _empty_state("Sem dados de série temporal para o período seleccionado.")
    else:
        pib_pico    = ago.get("PIB_2014_USD_Bilhões", pib_ago_display)
        boom_cresc  = ago.get("Crescimento_Boom_Commodities_%", 0)
        insight(
            f"Angola atingiu o pico de <strong>${pib_pico:.0f}B</strong> em 2014, "
            f"impulsionado pelo boom do petróleo (+{boom_cresc:.0f}% em 2000–2006). "
            f"A queda do petróleo (2014–16) e a COVID-19 (-{abs(ago['Impacto_COVID_%']):.1f}%) "
            f"reduziram o PIB para ${ago['PIB_2020_USD_Bilhões']:.0f}B. Recuperação em curso.",
            "angola",
        )

        fig5 = fig_base(height=380)
        add_era_highlight(fig5, filtro_era, s)  # highlight usa `s` completo para calcular limites

        for iso, nome in PEERS_N.items():
            if iso not in peers_no_grupo:
                continue
            df_i = s_peers[s_peers["Código_ISO3"] == iso]
            if df_i.empty:
                continue
            cor   = PEERS_C[nome]
            width = 3 if iso == "AGO" else 1.8
            fig5.add_trace(go.Scatter(
                x=df_i["Ano"], y=df_i["PIB_USD_Bilhões"],
                mode="lines+markers", name=nome,
                line=dict(color=cor, width=width),
                marker=dict(size=7 if iso == "AGO" else 5),
                hovertemplate=f"<b>{nome} %{{x}}</b><br>PIB: $%{{y:.1f}}B<extra></extra>",
            ))

        anos_peers = sorted(int(a) for a in s_peers["Ano"].unique())
        for ano, label, cor in [
            (2006, f"Boom +{boom_cresc:.0f}%", ANGOLA),
            (2014, "Queda petróleo", RED),
            (2020, f"COVID {ago['Impacto_COVID_%']:.1f}%", RED),
        ]:
            if ano in anos_peers:
                add_vline(fig5, ano, label, cor)

        fig5.update_xaxes(tickmode="array", tickvals=anos_peers)
        fig5.update_yaxes(title=dict(text="PIB ($B)", font=dict(color=MUTED, size=10)))
        st.plotly_chart(fig5, use_container_width=True)

    # ── Gráfico 6 + 7 ─────────────────────────────────────────────────────────
    col6, col7 = st.columns(2)

    with col6:
        n_label = f"{n_grupo} Países" if filtro_vuln != "Todos" else "30 Países"
        section(f"PIBpc vs Crescimento Acumulado {n_label}", badge="quadrantes analíticos")

        # Médias do grupo filtrado (linhas de quadrante reactivas)
        media_cresc = grupo_cresc
        media_pibpc = grupo_pibpc

        q = (
            "alto crescimento + PIBpc abaixo da média do grupo"
            if cresc_era_ago >= media_cresc and ago["PIB_por_Habitante_2023_USD"] < media_pibpc
            else "outro quadrante"
        )
        insight(
            f"No contexto do <strong>{label_grupo}</strong>, Angola posiciona-se no quadrante de "
            f"<strong>{q}</strong>. Cresceu <strong>+{cresc_era_ago:.0f}%</strong> vs média "
            f"+{media_cresc:.0f}% do grupo. PIBpc ${ago['PIB_por_Habitante_2023_USD']:,} "
            f"vs média ${media_pibpc:,.0f}.",
            "angola",
        )

        # Scatter com países do grupo filtrado + Angola sempre visível
        pf2 = pf.copy()
        pf2["Destaque"] = pf2["Código_ISO3"].apply(lambda x: "Angola" if x == "AGO" else "Grupo")

        if pf2.empty:
            _empty_state("Sem países no grupo filtrado.")
        else:
            fig6 = px.scatter(
                pf2,
                x="Crescimento_Acumulado_2000_2023_%",
                y="PIB_por_Habitante_2023_USD",
                size="PIB_2023_USD_Bilhões",
                color="Destaque",
                hover_name="País",
                color_discrete_map={"Angola": ANGOLA, "Grupo": BLUE},
                labels={
                    "Crescimento_Acumulado_2000_2023_%": "Crescimento Acumulado (%)",
                    "PIB_por_Habitante_2023_USD": "PIBpc 2023 (USD)",
                },
                size_max=50,
            )

            xmax = pf2["Crescimento_Acumulado_2000_2023_%"].max() * 1.05
            ymax = pf2["PIB_por_Habitante_2023_USD"].max() * 1.08
            label_cor = "rgba(255,255,255,0.13)"

            for xi, yi, label in [
                (media_cresc / 2, ymax * 0.95,       "Crescimento baixo<br>PIBpc alto"),
                (xmax * 0.75,     ymax * 0.95,       "Crescimento alto<br>PIBpc alto"),
                (media_cresc / 2, media_pibpc * 0.2, "Crescimento baixo<br>PIBpc baixo"),
                (xmax * 0.75,     media_pibpc * 0.2, "Crescimento alto<br>PIBpc baixo"),
            ]:
                fig6.add_annotation(
                    x=xi, y=yi, text=label, showarrow=False,
                    font=dict(size=8, color=label_cor), align="center",
                )

            fig6.add_vline(
                x=media_cresc, line_dash="dash", line_color=MUTED, line_width=1,
                annotation_text=f"Média grupo {media_cresc:.0f}%",
                annotation_font_color=MUTED, annotation_position="top left",
                annotation_font_size=9,
            )
            fig6.add_hline(
                y=media_pibpc, line_dash="dash", line_color=MUTED, line_width=1,
                annotation_text=f"PIBpc grupo ${media_pibpc:,.0f}",
                annotation_font_color=MUTED, annotation_position="bottom right",
                annotation_font_size=9,
            )
            fig6.add_annotation(
                x=ago["Crescimento_Acumulado_2000_2023_%"] + 20,
                y=ago["PIB_por_Habitante_2023_USD"],
                text="Angola", showarrow=True, arrowhead=2,
                arrowcolor=ANGOLA, arrowsize=0.8, arrowwidth=1.5,
                font=dict(color=ANGOLA, size=11, weight=700), ax=40, ay=-20,
            )
            fig6.update_layout(
                paper_bgcolor=CARD, plot_bgcolor=CARD, height=380,
                margin=dict(l=12, r=12, t=12, b=12),
                font=dict(color=MUTED, size=11),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED, size=10)),
                xaxis=dict(gridcolor=GRID, zeroline=False),
                yaxis=dict(gridcolor=GRID, zeroline=False),
                hoverlabel=dict(bgcolor="#1A1A2E", font_color=WHITE),
            )
            st.plotly_chart(fig6, use_container_width=True)

    with col7:
        # Top 5 do grupo filtrado por crescimento (Angola incluída sempre)
        top5_pool = pf.sort_values("Crescimento_Acumulado_2000_2023_%", ascending=False)
        # Garante Angola no conjunto mesmo que não esteja no top5 natural
        top5_sem_ago = top5_pool[top5_pool["Código_ISO3"] != "AGO"].head(4)
        ago_row      = top5_pool[top5_pool["Código_ISO3"] == "AGO"]
        top5         = (
            import_concat([top5_sem_ago, ago_row])
            .sort_values("Crescimento_Acumulado_2000_2023_%", ascending=False)
        ) if not ago_row.empty else top5_sem_ago

        section(f"Crescimento Acumulado: Angola vs Top do {label_grupo}", badge="2000–2023")

        if top5.empty:
            _empty_state("Sem dados de crescimento para o grupo filtrado.")
        else:
            angola_pos = list(top5["Código_ISO3"]).index("AGO") + 1 if "AGO" in top5["Código_ISO3"].values else "N/A"
            insight(
                f"No grupo <strong>{label_grupo}</strong>, Angola (+{cresc_era_ago:.0f}%) "
                f"ocupa a posição <strong>{angola_pos}ª</strong> em crescimento. "
                f"Partiu de uma base de <strong>${pib_ago_base:.1f}B</strong> em {label_ano_base}.",
                "angola",
            )

            cores = [ANGOLA if x == "AGO" else BLUE for x in top5["Código_ISO3"]]
            fig7  = fig_base(height=340)
            fig7.add_trace(go.Bar(
                x=top5["País"], y=top5["Crescimento_Acumulado_2000_2023_%"],
                marker=dict(color=cores, line=dict(width=0)),
                text=top5["Crescimento_Acumulado_2000_2023_%"].apply(lambda v: f"+{v:.0f}%"),
                textposition="outside",
                textfont=dict(color=WHITE, size=10, family="JetBrains Mono"),
                hovertemplate="<b>%{x}</b><br>Crescimento: +%{y:.1f}%<extra></extra>",
            ))
            fig7.add_hline(
                y=grupo_cresc, line_dash="dash", line_color=MUTED, line_width=1,
                annotation_text=f"Média {label_grupo} +{grupo_cresc:.0f}%",
                annotation_font_color=MUTED, annotation_position="bottom right",
                annotation_font_size=9,
            )
            fig7.update_yaxes(showticklabels=False)
            st.plotly_chart(fig7, use_container_width=True)

    # ── Gráfico 8 — Tabela + Radar ────────────────────────────────────────────
    col8, colm = st.columns([3, 2])

    with col8:
        section(f"Comparação — Angola vs Top {label_grupo}", badge="análise multidimensional")

        # Tabela: Angola + top 5 por PIB do grupo filtrado
        tabela_pool = pf.sort_values("Ranking_PIB_2023")
        tabela_df   = tabela_pool.head(6)   # top 6 do grupo (inclui Angola se estiver)

        # Garante Angola mesmo que fora do top6
        if "AGO" not in tabela_df["Código_ISO3"].values and not ago_row.empty:
            tabela_df = import_concat([tabela_df, ago_row]).drop_duplicates("Código_ISO3")

        if tabela_df.empty:
            _empty_state("Sem dados para a tabela comparativa.")
        else:
            colunas = {
                "País":                              "País",
                "PIB_2023_USD_Bilhões":              "PIB 2023 ($B)",
                "PIB_por_Habitante_2023_USD":        "PIBpc (USD)",
                "Crescimento_Acumulado_2000_2023_%": "Cresc. Acum. (%)",
                "Inflação_2022_%":                   "Inflação (%)",
                "Recuperacao_COVID_%":               "Rec. COVID (%)",
            }
            tv = tabela_df[list(colunas.keys())].rename(columns=colunas).reset_index(drop=True)

            def estilo_linha(row):
                if row["País"] == "Angola":
                    return [f"background-color:#180A00;color:{ANGOLA};font-weight:700;"] * len(row)
                return [""] * len(row)

            def estilo_cols(df):
                styles = df.copy().map(lambda _: "")
                for col in ["Cresc. Acum. (%)", "Rec. COVID (%)"]:
                    if col in df.columns:
                        mx = df[col].max()
                        mn = df[col].min()
                        for i, v in enumerate(df[col]):
                            if df["País"].iloc[i] != "Angola":
                                intensity = int(60 * (v - mn) / (mx - mn + 0.001))
                                styles.loc[i, col] = f"color: rgb({80+intensity},{80+intensity},{200+intensity//2})"
                return styles

            styled = (
                tv.style
                .apply(estilo_linha, axis=1)
                .apply(estilo_cols, axis=None)
                .format({
                    "PIB 2023 ($B)":    "{:.1f}",
                    "PIBpc (USD)":      "{:,.0f}",
                    "Cresc. Acum. (%)": "+{:.1f}",
                    "Inflação (%)":     "{:.1f}",
                    "Rec. COVID (%)":   "+{:.1f}",
                })
                .set_properties(**{
                    "background-color": CARD,
                    "color": WHITE,
                    "border-color": BORDER,
                    "font-size": "12px",
                })
                .set_table_styles([{"selector": "th", "props": [
                    ("background-color", "#0A0A16"), ("color", MUTED),
                    ("font-size", "10px"), ("font-weight", "600"),
                    ("text-transform", "uppercase"), ("letter-spacing", ".08em"),
                    ("border-color", BORDER), ("padding", "8px 12px"),
                ]}])
            )
            st.dataframe(styled, use_container_width=True, hide_index=True)

    with colm:
        section("Perfil Macroeconómico: Angola", badge="radar comparativo")

        ago_data = m["p"][m["p"]["Código_ISO3"] == "AGO"]
        if ago_data.empty:
            _empty_state("Dados de Angola não disponíveis.")
        else:
            ago_data   = ago_data.iloc[0]
            n_paises   = len(pf)

            # Rankings recalculados dentro do grupo filtrado
            rank_pib    = int(pf.sort_values("PIB_2023_USD_Bilhões", ascending=False).reset_index(drop=True).index[pf["Código_ISO3"].values == "AGO"][0]) + 1 if "AGO" in pf["Código_ISO3"].values else int(ago_data["Ranking_PIB_2023"])
            rank_pibpc  = int(pf.sort_values("PIB_por_Habitante_2023_USD", ascending=False).reset_index(drop=True).index[pf["Código_ISO3"].values == "AGO"][0]) + 1 if "AGO" in pf["Código_ISO3"].values else int(ago_data["Ranking_PIBpc_2023"])
            rank_cresc  = int(pf.sort_values("Crescimento_Acumulado_2000_2023_%", ascending=False).reset_index(drop=True).index[pf["Código_ISO3"].values == "AGO"][0]) + 1 if "AGO" in pf["Código_ISO3"].values else int(ago_data["Ranking_Crescimento_Acumulado"])

            denom = max(n_paises - 1, 1)
            dims = {
                "PIB (rank inv.)":   1 - (rank_pib   - 1) / denom,
                "PIBpc (rank inv.)": 1 - (rank_pibpc - 1) / denom,
                "Crescimento":       1 - (rank_cresc  - 1) / denom,
                "Estabilidade":      1 - min(ago_data["Score_Vuln"] / 3, 1),
                "Rec. COVID":        min(ago_data["Recuperacao_COVID_%"] / 100, 1),
            }

            cats = list(dims.keys()) + [list(dims.keys())[0]]
            vals = list(dims.values()) + [list(dims.values())[0]]

            fig_r = go.Figure(go.Scatterpolar(
                r=vals, theta=cats, fill="toself",
                fillcolor="rgba(232,114,10,0.15)",
                line=dict(color=ANGOLA, width=2),
                marker=dict(size=6, color=ANGOLA),
                hovertemplate="<b>%{theta}</b><br>Score: %{r:.2f}<extra></extra>",
            ))
            fig_r.update_layout(
                polar=dict(
                    bgcolor=CARD_L,
                    radialaxis=dict(
                        visible=True, range=[0, 1],
                        tickfont=dict(size=8, color=MUTED),
                        gridcolor=GRID, linecolor=BORDER,
                        tickvals=[0.25, 0.5, 0.75, 1.0],
                        ticktext=["25%", "50%", "75%", "100%"],
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=10, color=MUTED_L),
                        linecolor=BORDER, gridcolor=GRID,
                    ),
                ),
                showlegend=False,
                paper_bgcolor=CARD, plot_bgcolor=CARD,
                height=340, margin=dict(l=20, r=20, t=20, b=20),
                font=dict(color=MUTED),
                hoverlabel=dict(bgcolor="#1A1A2E", font_color=WHITE),
            )
            insight(
                f"No grupo <strong>{label_grupo}</strong>, Angola é #<strong>{rank_cresc}</strong> "
                f"em crescimento e #<strong>{rank_pib}</strong> em PIB. "
                f"Estabilidade limitada por inflação de {ago_data['Inflação_2022_%']:.1f}% "
                f"e dívida de {ago_data['Dívida_Pública_%_PIB_2022']:.1f}% do PIB.",
                "angola",
            )
            st.plotly_chart(fig_r, use_container_width=True)


# ── Utilitário interno (evita import pandas no topo só para concat) ───────────
import pandas as _pd
def import_concat(dfs): return _pd.concat(dfs, ignore_index=True)