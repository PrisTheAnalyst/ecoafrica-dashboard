import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from components import kpi, insight, section, fig_base
from config import (ANGOLA, BLUE, BLUE_L, GREEN, GOLD, RED,
                    WHITE, MUTED, MUTED_L, CARD, CARD_L, GRID, BORDER)


# ── Dados embutidos (extraídos do xlsx — Dicionario de Dados + KPIs Resumo) ──
DICIONARIO = [
    ("Código_ISO3",                   "Texto",               "Código ISO de 3 letras que identifica o país internacionalmente (ex: AGO = Angola).",              "ISO 3166-1"),
    ("País",                          "Texto",               "Nome do país em português.",                                                                       "World Bank Open Data"),
    ("Região",                        "Categórico",          "Agrupamento geográfico dentro de África: Norte, Sul, Este, Oeste ou Centro.",                      "União Africana"),
    ("Capital",                       "Texto",               "Cidade sede do governo do país.",                                                                   "World Bank Open Data"),
    ("Grupo_Renda_Banco_Mundial",     "Categórico",          "Classificação do Banco Mundial pelo rendimento médio da população (Baixa, Média-Baixa, Média-Alta, Alta).", "World Bank Open Data"),
    ("Idioma_Oficial",                "Texto",               "Língua ou línguas oficialmente reconhecidas pelo governo.",                                        "World Bank Open Data"),
    ("PIB_XXXX_USD_Bilhões",          "Moeda (USD B)",       "Riqueza total produzida pelo país naquele ano, em mil milhões de dólares.",                        "World Bank — NY.GDP.MKTP.CD ÷ 1 000 000 000"),
    ("PIB_por_Habitante_XXXX_USD",    "Moeda (USD)",         "Se a riqueza fosse dividida igualmente, quanto caberia a cada pessoa.",                            "World Bank — NY.GDP.PCAP.CD"),
    ("Crescimento_PIB_XXXX_%",        "Percentagem",         "Quanto a economia cresceu ou encolheu face ao ano anterior. Negativo = recessão.",                 "World Bank — NY.GDP.MKTP.KD.ZG"),
    ("Inflação_2022_%",               "Percentagem",         "Quanto os preços subiram em média, inflação alta corrói o poder de compra.",                      "World Bank — FP.CPI.TOTL.ZG"),
    ("Dívida_Pública_%_PIB_2022",     "Percentagem",         "Quanto o governo deve em proporção ao tamanho da economia. Acima de 100% = risco fiscal elevado.", "World Bank — GC.DOD.TOTL.GD.ZS"),
    ("IDE_Entrada_2022_USD_Bilhões",  "Moeda (USD B)",       "Investimento directo estrangeiro recebido, quanto maior for mais confiança dos investidores.",       "World Bank — BX.KLT.DINV.CD.WD ÷ 1 000 000 000"),
    ("Populacao_2022_Milhões",        "Número (M)",          "Número de habitantes em 2022, em milhões.",                                                        "World Bank — SP.POP.TOTL ÷ 1 000 000"),
    ("Crescimento_Acumulado_2000_2023_%", "Percentagem",     "Crescimento total da economia entre 2000 e 2023, trajectória de longo prazo.",                   "(PIB_2023 − PIB_2000) / PIB_2000 × 100"),
    ("Crescimento_Boom_Commodities_%","Percentagem",         "Crescimento durante o boom das matérias-primas (2000–2006).",                                      "(PIB_2006 − PIB_2000) / PIB_2000 × 100"),
    ("Impacto_Crise_2009_%",          "Percentagem",         "Variação durante a crise financeira global (2006–2009). Negativo = recessão.",                     "(PIB_2009 − PIB_2006) / PIB_2006 × 100"),
    ("Crescimento_Africa_Rising_%",   "Percentagem",         "Crescimento na fase 'Africa Rising' (2010–2014).",                                                 "(PIB_2014 − PIB_2010) / PIB_2010 × 100"),
    ("Impacto_COVID_%",               "Percentagem",         "Quanto a economia perdeu em 2020 face a 2019: impacto directo da pandemia.",                      "(PIB_2020 − PIB_2019) / PIB_2019 × 100"),
    ("Recuperacao_COVID_%",           "Percentagem",         "Comparação do PIB de 2022 com o nível pré-pandemia de 2019.",                                      "(PIB_2022 − PIB_2019) / PIB_2019 × 100"),
    ("Crescimento_PIBpc_2000_2023_%", "Percentagem",         "Crescimento do PIB por habitante em 23 anos: indica melhoria do nível de vida.",                  "(PIBpc_2023 − PIBpc_2000) / PIBpc_2000 × 100"),
    ("Perfil_Económico",              "Categórico",          "Tamanho da economia: Grande (≥$200B), Em Destaque (≥$80B), Emergente (≥$30B), Em Desenvolvimento (<$30B).", "Regra baseada no PIB 2023"),
    ("Status_COVID",                  "Categórico",          "Se o país recuperou economicamente ao nível pré-pandemia.",                                        "Rec.COVID > 5% = Superou | 0–5% = Recuperou | <0% = Ainda abaixo"),
    ("Ranking_PIB_2023",              "Inteiro",             "Posição entre os 30 países pelo PIB total em 2023. #1 = maior economia.",                          "Rank denso descendente sobre PIB_2023"),
    ("Ranking_PIBpc_2023",            "Inteiro",             "Posição pelo PIB por habitante em 2023. #1 = maior riqueza per capita.",                           "Rank denso descendente sobre PIB_por_Habitante_2023"),
    ("Ranking_Crescimento_Acumulado", "Inteiro",             "Posição pelo crescimento acumulado desde 2000. #1 = maior crescimento.",                           "Rank denso descendente sobre Crescimento_Acumulado_2000_2023"),
    ("Era_Económica",                 "Categórico",          "Período histórico que contextualiza os dados da série temporal.",                                  "Definição editorial EcoÁfrica"),
    ("Ordem_Era",                     "Inteiro",             "Número de ordenação cronológica das eras económicas.",                                              "Definição editorial EcoÁfrica"),
    ("Score_Vuln",                    "Decimal",             "Índice de vulnerabilidade macroeconómica calculado a partir da inflação e dívida pública normalizadas.", "Score_Vuln = (Inflação/Média × 0.5) + (Dívida/Média × 0.5)"),
]

KPIS_RESUMO = [
    ("PIB Total África 2023",                   "$2 765,1 B USD",    "Soma do PIB de 30 países africanos em 2023"),
    ("PIB Total África 2000",                   "$704,8 B USD",      "Soma do PIB dos mesmos 30 países no ano 2000"),
    ("Crescimento Total do Continente",         "+292,3%",           "A África cresceu quase 4× em tamanho económico em 23 anos"),
    ("Maior Economia (PIB Total) 2023",         "Nigéria ($497B)",   "O país com a maior economia medida pelo total produzido"),
    ("Maior PIB por Habitante 2023",            "Maurícias ($13.2K)","O país onde cada pessoa tem em média mais riqueza gerada"),
    ("País com Maior Crescimento Acumulado",    "Etiópia (+1800%)",  "O país que mais multiplicou a sua economia desde 2000"),
    ("País com Maior Crescimento Anual (2023)", "Senegal (+8,3%)",   "O país que mais cresceu em percentagem no último ano"),
    ("País com Maior Inflação 2022",            "Zimbabué (285%)",   "Alta inflação significa que os preços sobem muito rapidamente"),
    ("Angola — PIB 2023",                       "$84,7 B USD",       "Tudo o que Angola produziu e vendeu em 2023"),
    ("Angola — PIB por Habitante 2023",         "$2 757 USD",        "Em média cada angolano gerou este valor em riqueza em 2023"),
    ("Angola — Crescimento Acumulado",          "+830,8%",           "Angola multiplicou a sua economia aproximadamente 9× desde 2000"),
    ("Angola — Ranking em África",              "#8 de 30",          "Posição de Angola entre as 30 maiores economias africanas"),
    ("Angola — Status COVID",                   "Superou o pré-COVID","Angola já recuperou economicamente do impacto da pandemia"),
]

ERAS = [
    ("Início das Séries",          "2000",       "Ponto de partida da análise. Economias africanas ainda em fase de estabilização pós-conflitos e ajustamentos estruturais."),
    ("Boom das Matérias-Primas",   "2000–2006",  "Boom global de commodities impulsionou petróleo, minérios e agricultura. Angola e Nigéria cresceram >38%."),
    ("Crise Financeira Global",    "2006–2009",  "Colapso do Lehman Brothers. Queda dos preços das commodities. Vários países africanos registaram recessão."),
    ("Africa Rising",              "2010–2014",  "Período de optimismo. FMI e economistas internacionais projectavam crescimento africano superior ao mundial."),
    ("Queda do Petróleo",          "2014–2019",  "Petróleo caiu de $110 para $50/barril. Angola, Nigéria e Argélia sofreram forte contracção."),
    ("COVID-19",                   "2019–2020",  "Pandemia global. PIB médio africano caiu −3,5%. Angola perdeu −5,4% do PIB em apenas um ano."),
    ("Recuperação Pós-COVID",      "2021–2023",  "Recuperação desigual. 60% dos países superaram os níveis de 2019. Inflação e dívida pública subiram."),
]


def render(p, s, r, m):
    st.markdown('<div class="page-title">Dicionário de Dados</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-desc">Guia de referência completo para todas as variáveis, métricas derivadas, '
        'eras económicas e KPIs do dataset EcoÁfrica 2000–2023.</div>',
        unsafe_allow_html=True,
    )

    # ── Tabs internas ─────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([" Variáveis", " Eras Económicas", " KPIs do Dataset"])

    # ── Tab 1 — Variáveis ─────────────────────────────────────────────────────
    with tab1:
        section("Glossário de Variáveis", badge=f"{len(DICIONARIO)} colunas")

        # Filtro por tipo
        tipos = sorted(set(t for _, t, _, _ in DICIONARIO))
        fc1, fc2 = st.columns([2, 4])
        with fc1:
            st.markdown('<div class="filter-label">Filtrar por Tipo</div>', unsafe_allow_html=True)
            tipo_sel = st.selectbox("Tipo", ["Todos"] + tipos, label_visibility="collapsed", key="dic_tipo")
        with fc2:
            st.markdown('<div class="filter-label">Pesquisar</div>', unsafe_allow_html=True)
            pesquisa = st.text_input("Pesquisar variável ou descrição", placeholder="ex: PIB, dívida, ranking…", label_visibility="collapsed", key="dic_search")

        dados_f = [
            (col, tipo, desc, origem)
            for col, tipo, desc, origem in DICIONARIO
            if (tipo_sel == "Todos" or tipo == tipo_sel)
            and (not pesquisa or pesquisa.lower() in col.lower() or pesquisa.lower() in desc.lower())
        ]

        if not dados_f:
            st.markdown(
                f'<div style="padding:1.5rem;text-align:center;color:{MUTED};'
                f'background:#0F0F1A;border:1px dashed #1E1E32;border-radius:10px;margin:.5rem 0">'
                f'Nenhuma variável encontrada para os filtros seleccionados.</div>',
                unsafe_allow_html=True,
            )
        else:
            # Badge de contagem
            st.markdown(
                f'<div style="color:{MUTED};font-size:11px;margin:.4rem 0 .8rem">'
                f'A mostrar <strong style="color:{WHITE}">{len(dados_f)}</strong> de {len(DICIONARIO)} variáveis</div>',
                unsafe_allow_html=True,
            )

            tipo_cores = {
                "Texto":        BLUE_L,
                "Categórico":   GOLD,
                "Moeda (USD B)":GREEN,
                "Moeda (USD)":  GREEN,
                "Percentagem":  ANGOLA,
                "Inteiro":      MUTED_L,
                "Decimal":      "#8A4FC8",
            }

            for col, tipo, desc, origem in dados_f:
                cor_tipo = tipo_cores.get(tipo, MUTED)
                st.markdown(f"""
                <div style="background:{CARD};border:1px solid {BORDER};border-left:3px solid {cor_tipo};
                            border-radius:0 10px 10px 0;padding:.8rem 1.1rem;margin-bottom:.5rem">
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
                        <code style="color:{WHITE};font-size:12px;font-weight:700;
                                     background:#1A1A2E;padding:2px 8px;border-radius:4px">{col}</code>
                        <span style="color:{cor_tipo};font-size:10px;font-weight:600;
                                     letter-spacing:.08em;text-transform:uppercase">{tipo}</span>
                    </div>
                    <div style="color:{MUTED_L};font-size:12px;line-height:1.6;margin-bottom:4px">{desc}</div>
                    <div style="color:{MUTED};font-size:10px">
                        <span style="color:{ANGOLA}">Origem:</span> {origem}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Tab 2 — Eras ─────────────────────────────────────────────────────────
    with tab2:
        section("Eras Económicas Africanas", badge="2000–2023")
        insight(
            "O dataset está segmentado em <strong>7 eras económicas</strong> que reflectem os principais "
            "ciclos globais e continentais que moldaram o crescimento africano nos últimos 23 anos.",
        )

        for i, (era, periodo, descricao) in enumerate(ERAS):
            cores_era = [BLUE_L, GOLD, RED, GREEN, RED, "#F87171", ANGOLA]
            cor = cores_era[i % len(cores_era)]
            st.markdown(f"""
            <div style="background:{CARD};border:1px solid {BORDER};border-radius:12px;
                        padding:1rem 1.3rem;margin-bottom:.6rem;display:flex;gap:1.2rem;align-items:flex-start">
                <div style="min-width:36px;height:36px;background:{cor}22;border:1px solid {cor}55;
                            border-radius:50%;display:flex;align-items:center;justify-content:center;
                            color:{cor};font-size:13px;font-weight:800;flex-shrink:0">{i+1}</div>
                <div>
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
                        <span style="color:{WHITE};font-size:13px;font-weight:700">{era}</span>
                        <span style="color:{cor};font-size:10px;background:{cor}18;
                                     padding:2px 8px;border-radius:4px;font-weight:600">{periodo}</span>
                    </div>
                    <div style="color:{MUTED_L};font-size:12px;line-height:1.6">{descricao}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Tab 3 — KPIs ─────────────────────────────────────────────────────────
    with tab3:
        section("KPIs Globais do Dataset", badge="resumo executivo")
        insight(
            "Valores de referência calculados sobre os <strong>30 países · 23 anos</strong> do dataset. "
            "Úteis como benchmark ao interpretar qualquer indicador individual."
        )

        # Angola vs continente em cards destaque
        ca1, ca2, ca3 = st.columns(3)
        with ca1: kpi("PIB Total África 2023", "$2 765 B",  "30 países combinados")
        with ca2: kpi("Crescimento Continente", "+292%",    "2000 → 2023", "green")
        with ca3: kpi("Angola vs Continente",   "+831%",    "quase 3× a média", "warn")

        st.markdown("<div style='margin:.5rem 0'></div>", unsafe_allow_html=True)

        for kpi_nome, valor, nota in KPIS_RESUMO:
            is_angola = "Angola" in kpi_nome
            borda = ANGOLA if is_angola else BORDER
            bg    = "#1A0F00" if is_angola else CARD
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {borda};border-radius:10px;
                        padding:.7rem 1.1rem;margin-bottom:.4rem;
                        display:flex;justify-content:space-between;align-items:center;gap:1rem">
                <div style="color:{MUTED_L};font-size:12px;flex:1">{kpi_nome}</div>
                <div style="color:{'#E8720A' if is_angola else WHITE};font-size:14px;
                            font-weight:700;font-variant-numeric:tabular-nums;
                            white-space:nowrap">{valor}</div>
                <div style="color:{MUTED};font-size:11px;flex:1;text-align:right">{nota}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(
            f'<div style="color:{MUTED};font-size:10px;margin-top:1rem;padding-top:.8rem;'
            f'border-top:1px solid {BORDER}">Fonte: World Bank Open Data · '
            f'Todos os valores em USD · Calculados sobre os 30 países incluídos no dataset EcoÁfrica.</div>',
            unsafe_allow_html=True,
        )