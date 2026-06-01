import os
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# DEBUG TEMPORÁRIO — remove depois
import streamlit as st
st.write("BASE_DIR:", BASE_DIR)
st.write("Ficheiros em BASE_DIR:", os.listdir(BASE_DIR))
st.write("Existe data/?", os.path.exists(os.path.join(BASE_DIR, "data")))


@st.cache_data
def load():
    p = pd.read_csv(os.path.join(BASE_DIR, "data", "paises.csv"),        sep=";", decimal=",")
    s = pd.read_csv(os.path.join(BASE_DIR, "data", "serie_temporal.csv"), sep=";", decimal=",")
    r = pd.read_csv(os.path.join(BASE_DIR, "data", "regioes.csv"),        sep=";", decimal=",")
    return p, s, r
