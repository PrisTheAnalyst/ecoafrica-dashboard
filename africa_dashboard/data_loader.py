import os
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@st.cache_data
def load():
    p = pd.read_csv(os.path.join(BASE_DIR, "data", "paises.csv"),        sep=";", decimal=",")
    s = pd.read_csv(os.path.join(BASE_DIR, "data", "serie_temporal.csv"), sep=";", decimal=",")
    r = pd.read_csv(os.path.join(BASE_DIR, "data", "regioes.csv"),        sep=";", decimal=",")
    return p, s, r


@st.cache_data
def compute_metrics(p, s):
    pib23       = p["PIB_2023_USD_Bilhões"].sum()
    pib00       = p["PIB_2000_USD_Bilhões"].sum()
    cresc_cont  = (pib23 - pib00) / pib00 * 100
    media_pibpc = p["PIB_por_Habitante_2023_USD"].mean()
    media_cresc = p["Crescimento_Acumulado_2000_2023_%"].mean()
    acima_media = (p["PIB_por_Habitante_2023_USD"] > media_pibpc).sum()
    maior_cresc = p.nlargest(1, "Crescimento_Acumulado_2000_2023_%")["País"].values[0]

    ago = p[p["Código_ISO3"] == "AGO"].iloc[0]

    inf_med = p["Inflação_2022_%"].mean()
    div_med = p["Dívida_Pública_%_PIB_2022"].mean()
    p = p.copy()
    p["Score_Vuln"] = (
        p["Inflação_2022_%"] / inf_med * 0.5 +
        p["Dívida_Pública_%_PIB_2022"].fillna(div_med) / div_med * 0.5
    )
    ago_score = p[p["Código_ISO3"] == "AGO"]["Score_Vuln"].values[0]

    return dict(
        pib23       = pib23,
        pib00       = pib00,
        cresc_cont  = cresc_cont,
        media_pibpc = media_pibpc,
        media_cresc = media_cresc,
        acima_media = acima_media,
        maior_cresc = maior_cresc,
        impacto_med = p["Impacto_COVID_%"].mean(),
        recup_med   = p["Recuperacao_COVID_%"].mean(),
        ago         = ago,
        ago_score   = ago_score,
        p           = p,
    )
