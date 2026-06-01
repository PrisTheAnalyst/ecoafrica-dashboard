import streamlit as st
import pandas as pd
from components import kpi, insight, section
from config import (ANGOLA, BLUE, BLUE_L, GREEN, RED, GOLD,
                    WHITE, MUTED, MUTED_L, CARD, BORDER)

CHANGELOG = [
    ("2025-01", "v1.0", "Lançamento",
     "Dashboard inicial com dados de 30 países. Abas: Capa, África e Angola.",
     []),
    ("2025-01", "v1.1", "Correcção",
     "Corrigidos bugs de indentação em _africa.py e _angola.py que impediam o render.",
     ["_africa.py", "_angola.py"]),
    ("2025-01", "v1.2", "Melhoria",
     "Filtros de Era Económica e Score de Vulnerabilidade tornados reactivos em toda a dash de Angola.",
     ["_angola.py"]),
    ("2025-01", "v1.3", "Nova Funcionalidade",
     "Adicionadas abas: Finanças Públicas, Dicionário de Dados e Extras.",
     ["financas.py", "dicionario.py", "extras.py", "app.py"]),
]

ROADMAP = [
    ("Q1 2025", "Planeado", BLUE_L, [
        "Actualização de dados para 2024 (World Bank release Q2)",
        "Adicionar 5 novos países: Comores, Djibouti, Eritreia, Somália, Sudão do Sul",
        "Exportação de gráficos como PNG directamente da interface",
    ]),
    ("Q2 2025", "Planeado", GOLD, [
        "Dashboard de Comércio Externo (exportações, importações, balança comercial)",
        "Integração com API do World Bank para dados em tempo real",
        "Modo de comparação manual entre dois países seleccionados",
    ]),
    ("Q3 2025", "Em avaliação", MUTED_L, [
        "Dashboard de Desenvolvimento Humano (IDH, esperança de vida, educação)",
        "Mapa interactivo com drill-down por país",
        "Layout responsivo para mobile",
    ]),
    ("Q4 2025", "Ideia", BORDER, [
        "Projecções com regressão simples (PIB estimado 2025-2030)",
        "Partilha de dashboard via link com filtros preservados",
        "Versão em inglês e francês",
    ]),
]

LIMITACOES = [
    ("Cobertura temporal",
     "Os dados cobrem apenas os anos 2000, 2006, 2009, 2010, 2014, 2015, 2019, 2020, 2021, 2022 e 2023. "
     "Não há dados anuais contínuos para todos os anos intermédios.",
     GOLD),
    ("IDE de Angola",
     "O valor de IDE para Angola em 2022 está ausente no dataset. "
     "Pode reflectir saída líquida de capital ou subnotificação ao World Bank.",
     GOLD),
    ("Dívida da Líbia",
     "O dado de dívida pública da Líbia para 2022 está ausente — situação de conflito interno "
     "limitou a recolha de dados fiscais.",
     GOLD),
    ("Cobertura de países",
     "O dataset cobre 30 dos 54 países africanos reconhecidos pela UA. "
     "Países mais pequenos ou com dados insuficientes foram excluídos.",
     MUTED_L),
    ("Score de Vulnerabilidade",
     "O Score_Vuln é calculado internamente com base na média do grupo de 30 países. "
     "Não é um indicador oficial do FMI ou World Bank.",
     MUTED_L),
    ("Valores em USD correntes",
     "Todos os valores de PIB estão em dólares correntes, não ajustados à inflação, "
     "o que pode distorcer comparações inter-temporais.",
     MUTED_L),
]

COR_TIPO = {
    "Lançamento":          GREEN,
    "Correcção":           RED,
    "Melhoria":            GOLD,
    "Nova Funcionalidade": ANGOLA,
}


def _card_changelog(data, versao, tipo, descricao, ficheiros):
    cor = COR_TIPO.get(tipo, MUTED)

    ficheiros_html = "".join(
        '<code style="background:#1A1A2E;color:' + BLUE_L + ';font-size:10px;'
        'padding:1px 6px;border-radius:3px;margin-right:4px">' + f + '</code>'
        for f in ficheiros
    )

    badge_tipo = (
        '<span style="color:' + cor + ';font-size:10px;font-weight:600;'
        'padding:2px 8px;border-radius:4px;margin-right:4px">' + tipo + '</span>'
    )
    badge_data = '<span style="color:' + MUTED + ';font-size:10px">' + data + '</span>'

    st.markdown(
        '<div style="background:' + CARD + ';border:1px solid ' + BORDER + ';'
        'border-left:3px solid ' + cor + ';border-radius:0 10px 10px 0;'
        'padding:.9rem 1.2rem;margin-bottom:.6rem">'
        '<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap">'
        '<span style="color:' + WHITE + ';font-size:13px;font-weight:700">v' + versao + '</span>'
        + badge_tipo + badge_data + ficheiros_html +
        '</div>'
        '<div style="color:' + MUTED_L + ';font-size:12px;line-height:1.6">' + descricao + '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _card_roadmap(trimestre, estado, cor, items):
    items_html = "".join(
        '<li style="color:' + MUTED_L + ';font-size:12px;margin-bottom:4px;line-height:1.5">'
        + item + '</li>'
        for item in items
    )
    badge_estado = (
        '<span style="color:' + cor + ';font-size:10px;font-weight:600;'
        'padding:2px 8px;border-radius:4px">' + estado + '</span>'
    )
    st.markdown(
        '<div style="background:' + CARD + ';border:1px solid ' + BORDER + ';'
        'border-radius:12px;padding:1rem 1.3rem;margin-bottom:.7rem">'
        '<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">'
        '<span style="color:' + WHITE + ';font-size:13px;font-weight:700">' + trimestre + '</span>'
        + badge_estado +
        '</div>'
        '<ul style="margin:0;padding-left:1.2rem">' + items_html + '</ul>'
        '</div>',
        unsafe_allow_html=True,
    )


def _card_limitacao(titulo, descricao, cor):
    st.markdown(
        '<div style="background:' + CARD + ';border:1px solid ' + BORDER + ';'
        'border-left:3px solid ' + cor + ';border-radius:0 10px 10px 0;'
        'padding:.8rem 1.1rem;margin-bottom:.5rem">'
        '<div style="color:' + WHITE + ';font-size:12px;font-weight:700;margin-bottom:4px">'
        + titulo + '</div>'
        '<div style="color:' + MUTED_L + ';font-size:12px;line-height:1.6">' + descricao + '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def render(p, s, r, m):
    st.markdown('<div class="page-title">Extras & Actualizações</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-desc">Registo de alterações, roadmap de funcionalidades futuras, '
        'limitações do dataset e notas técnicas do projecto EcoÁfrica.</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["Changelog", "Roadmap", "Limitacoes & Notas"])

    with tab1:
        section("Histórico de Versões", badge="v" + CHANGELOG[-1][1])
        for data, versao, tipo, descricao, ficheiros in reversed(CHANGELOG):
            _card_changelog(data, versao, tipo, descricao, ficheiros)

    with tab2:
        section("Roadmap de Desenvolvimento", badge="2025")
        insight(
            "As funcionalidades abaixo estão sujeitas a alteração conforme disponibilidade de dados "
            "e prioridade do projecto."
        )
        for trimestre, estado, cor, items in ROADMAP:
            _card_roadmap(trimestre, estado, cor, items)

        st.markdown("<div style='margin:1.2rem 0 .4rem'></div>", unsafe_allow_html=True)
        section("Deixar Sugestão", badge="opcional")
        with st.form("form_sugestao", clear_on_submit=True):
            sugestao = st.text_area(
                "Descreva a funcionalidade ou melhoria que gostaria de ver",
                placeholder="Ex: Adicionar comparação entre dois países seleccionados...",
                height=90,
            )
            cat = st.selectbox(
                "Categoria",
                ["Nova Funcionalidade", "Melhoria de Gráfico", "Correcção de Dados", "UX/Interface", "Outro"],
            )
            enviado = st.form_submit_button("Enviar Sugestão", use_container_width=True)
            if enviado and sugestao.strip():
                st.success("Sugestão registada na categoria **" + cat + "**. Obrigado pelo contributo!")
            elif enviado:
                st.warning("Por favor, escreva a sua sugestão antes de enviar.")

    with tab3:
        section("Limitações do Dataset", badge=str(len(LIMITACOES)) + " notas")
        insight(
            "Estas limitações são importantes para uma interpretação correcta dos dados. "
            "Valores em falta estão sinalizados no dataset."
        )
        for titulo, descricao, cor in LIMITACOES:
            _card_limitacao(titulo, descricao, cor)

        st.markdown("<div style='margin:.8rem 0'></div>", unsafe_allow_html=True)
        section("Metadados do Projecto")

        n_paises = len(p)
        n_anos   = len(s["Ano"].unique())
        n_vars   = len(p.columns)
        n_obs    = len(s)

        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1: kpi("Países",       str(n_paises), "africanos no dataset")
        with mc2: kpi("Anos na série", str(n_anos),  "pontos temporais")
        with mc3: kpi("Variáveis",    str(n_vars),   "por país")
        with mc4: kpi("Observações",  str(n_obs),    "série temporal total")

        st.markdown(
            '<div style="color:' + MUTED + ';font-size:10px;margin-top:1rem;padding-top:.8rem;'
            'border-top:1px solid ' + BORDER + '">'
            'Fonte: World Bank Open Data · Dataset compilado para fins educativos · '
            'EcoÁfrica Dashboard.</div>',
            unsafe_allow_html=True,
        )