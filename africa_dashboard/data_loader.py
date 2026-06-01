import os
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load():
    p = pd.read_csv(os.path.join(BASE_DIR, "data", "paises.csv"),         sep=";", decimal=",")
    s = pd.read_csv(os.path.join(BASE_DIR, "data", "serie_temporal.csv"),  sep=";", decimal=",")
    r = pd.read_csv(os.path.join(BASE_DIR, "data", "regioes.csv"),         sep=";", decimal=",")
    return p, s, r

@st.cache_data
def load_dicionario():
    xl = os.path.join(BASE_DIR, "data", "africa_pib_completo_2000_2023_final.xlsx")
    dd = pd.read_excel(xl, sheet_name="Dicionario de Dados")
    kp = pd.read_excel(xl, sheet_name="KPIs Resumo")
    return dd, kp

@st.cache_data
def compute_metrics(p, s):
    p = p.copy()

    pib23       = float(p["PIB_2023_USD_Bilhões"].sum())
    pib00       = float(p["PIB_2000_USD_Bilhões"].sum())
    cresc_cont  = (pib23 - pib00) / pib00 * 100
    media_pibpc = float(p["PIB_por_Habitante_2023_USD"].mean())
    media_cresc = float(p["Crescimento_Acumulado_2000_2023_%"].mean())
    acima_media = int((p["PIB_por_Habitante_2023_USD"] > media_pibpc).sum())
    maior_cresc = p.nlargest(1, "Crescimento_Acumulado_2000_2023_%")["País"].values[0]

    inf_med = float(p["Inflação_2022_%"].mean())
    div_med = float(p["Dívida_Pública_%_PIB_2022"].mean())

    p["Score_Vuln"] = (
        p["Inflação_2022_%"] / inf_med * 0.5
        + p["Dívida_Pública_%_PIB_2022"].fillna(div_med) / div_med * 0.5
    )

    def nivel_risco(v):
        if v >= 2.0: return "Crítico"
        if v >= 1.5: return "Alto"
        if v >= 1.0: return "Moderado"
        return "Baixo"

    p["Nivel_Risco"] = p["Score_Vuln"].apply(nivel_risco)

    ago       = p[p["Código_ISO3"] == "AGO"].iloc[0]
    ago_score = float(p[p["Código_ISO3"] == "AGO"]["Score_Vuln"].values[0])

    return dict(
        pib23       = pib23,
        pib00       = pib00,
        cresc_cont  = cresc_cont,
        media_pibpc = media_pibpc,
        media_cresc = media_cresc,
        acima_media = acima_media,
        maior_cresc = maior_cresc,
        impacto_med = float(p["Impacto_COVID_%"].mean()),
        recup_med   = float(p["Recuperacao_COVID_%"].mean()),
        inf_med     = inf_med,
        div_med     = div_med,
        ago         = ago,
        ago_score   = ago_score,
        p           = p,
    )
