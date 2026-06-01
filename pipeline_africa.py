import os
import re
import sys
import pandas as pd
import numpy as np

# ========================= CONFIGURAÇÕES =========================

SOURCE = "africa_pib_completo_2000_2023_final.xlsx"
OUT_DIR = "output_powerbi"

NULOS_ACEITES = {
    "Dívida_Pública_%_PIB_2022":     "Líbia — dado indisponível",
    "IDE_Entrada_2022_USD_Bilhões":  "8 países não reportaram ao World Bank",
}

ERAS = {
    2000: ("Início das Séries",        1),
    2006: ("Boom das Matérias-Primas", 2),
    2009: ("Crise Financeira Global",  3),
    2010: ("Expansão Pós-Crise",       4),
    2014: ("Africa Rising",            5),
    2015: ("Choques e Ajustamentos",   6),
    2019: ("Pré-COVID",                7),
    2020: ("Pandemia COVID-19",        8),
    2021: ("Recuperação Inicial",      9),
    2022: ("Recuperação Consolidada", 10),
    2023: ("Recuperação Pós-COVID",   11),
}

_erros = []

# ========================= FUNÇÕES AUXILIARES =========================

def _log(nivel, msg):
    tags = {"ok": "OK ", "err": "ERR", "inf": "INF"}
    print(f"  {tags[nivel]} — {msg}")
    if nivel == "err":
        _erros.append(msg)


def _section(n, title):
    print(f"\n[{n}] {title}")


def _col_map(df):
    """Devolve dicionários {ano: coluna} para PIB, PIBpc e Crescimento."""
    pib, pibpc, cresc = {}, {}, {}
    for col in df.columns:
        if m := re.search(r'PIB_(\d{4})_USD_Bilhões$', col):
            pib[int(m.group(1))] = col
        if m := re.search(r'PIB_por_Habitante_(\d{4})_USD$', col):
            pibpc[int(m.group(1))] = col
        if m := re.search(r'Crescimento_PIB_(\d{4})_%$', col):
            cresc[int(m.group(1))] = col
    return pib, pibpc, cresc


def _round1(v):
    return round(float(v), 1) if pd.notna(v) else None


def _to_int(series):
    return pd.to_numeric(series, errors="coerce").round(0).astype("Int64")


def _to_float1(series):
    return pd.to_numeric(series, errors="coerce").round(1)


# ========================= 1. EXTRAÇÃO =========================

def extrair():
    _section(1, "EXTRACÇÃO")
    if not os.path.exists(SOURCE):
        sys.exit(f"Ficheiro não encontrado: {SOURCE}")

    paises  = pd.read_excel(SOURCE, sheet_name="Paises - Dados Completos")
    regioes = pd.read_excel(SOURCE, sheet_name="Regioes")

    _log("ok", f"paises   — {len(paises)} linhas | {len(paises.columns)} colunas")
    _log("ok", f"regioes  — {len(regioes)} linhas | {len(regioes.columns)} colunas")
    return paises, regioes


# ========================= 2. VALIDAÇÃO =========================

def validar(paises, regioes):
    _section(2, "VALIDAÇÃO")

    for nome, df in [("paises", paises), ("regioes", regioes)]:
        n = df.duplicated().sum()
        _log("err" if n else "ok", f"Duplicados em {nome}: {n}" if n else f"Sem duplicados em {nome}")

    for col, n in paises.isnull().sum()[paises.isnull().sum() > 0].items():
        if col in NULOS_ACEITES:
            _log("inf", f"Nulo aceite — {col}: {n}  ({NULOS_ACEITES[col]})")
        else:
            _log("err", f"Nulo inesperado — {col}: {n}")

    pib_cols = [c for c in paises.columns if re.match(r'PIB_\d{4}_USD_Bilhões$', c)]
    negativos = sum((paises[c] < 0).sum() for c in pib_cols)
    _log("err" if negativos else "ok", f"PIB negativos: {negativos}" if negativos else "Nenhum PIB negativo")

    _log("ok" if "AGO" in paises["Código_ISO3"].values else "err", "Angola presente")

    for col_p, col_r in [("PIB_2023_USD_Bilhões", "PIB_Total_2023_Bi"),
                         ("PIB_2000_USD_Bilhões", "PIB_Total_2000_Bi")]:
        tp = round(paises[col_p].sum(), 1)
        tr = round(regioes[col_r].sum(), 1)
        if abs(tp - tr) > 0.5:
            _log("err", f"Divergência {col_p}: paises=${tp}B vs regioes=${tr}B")
        else:
            _log("ok", f"Totais consistentes — {col_p}: ${tp}B")


# ========================= 3. TRANSFORMAÇÃO - PAÍSES =========================

def transformar_paises(df):
    _section(3, "TRANSFORMAÇÃO — PAISES")
    df = df.copy()

    # Limpeza de strings
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].str.strip()

    # Rankings (com tratamento seguro de NaN)
    df["Ranking_PIB_2023"] = df["PIB_2023_USD_Bilhões"].rank(ascending=False, method="min")
    df["Ranking_PIBpc_2023"] = df["PIB_por_Habitante_2023_USD"].rank(ascending=False, method="min")
    df["Ranking_Crescimento_Acumulado"] = df["Crescimento_Acumulado_2000_2023_%"].rank(ascending=False, method="min")

    df["Ranking_PIB_2023"] = _to_int(df["Ranking_PIB_2023"])
    df["Ranking_PIBpc_2023"] = _to_int(df["Ranking_PIBpc_2023"])
    df["Ranking_Crescimento_Acumulado"] = _to_int(df["Ranking_Crescimento_Acumulado"])

    # Tooltip para mapa
    df["Tooltip_Mapa"] = (
        df["País"] +
        " | PIB 2023: $" + df["PIB_2023_USD_Bilhões"].apply(lambda v: f"{v:.1f}" if pd.notna(v) else "N/D") + "B" +
        " | Crescimento: +" + df["Crescimento_Acumulado_2000_2023_%"].apply(lambda v: f"{v:.1f}" if pd.notna(v) else "N/D") + "%" +
        " | Região: " + df["Região"] +
        " | Ranking: #" + df["Ranking_PIB_2023"].astype(str)
    )

    df["Cor_Destaque"] = df["Código_ISO3"].apply(lambda x: "Angola" if x == "AGO" else "Outros")
    df["Top10_PIB_2023"] = df["Código_ISO3"].isin(
        df.nlargest(10, "PIB_2023_USD_Bilhões")["Código_ISO3"]
    ).map({True: "Top 10", False: "Fora Top 10"})

    # Grupo de crescimento
    p33 = df["Crescimento_Acumulado_2000_2023_%"].quantile(0.33)
    p66 = df["Crescimento_Acumulado_2000_2023_%"].quantile(0.66)
    df["Grupo_Crescimento"] = pd.cut(
        df["Crescimento_Acumulado_2000_2023_%"],
        bins=[-np.inf, p33, p66, np.inf],
        labels=["Baixo", "Médio", "Alto"]
    ).astype(str)

    # Tipagem final
    int_cols = [c for c in df.columns if re.search(r'PIB_por_Habitante_\d{4}_USD$', c)] + \
               ["Ranking_PIB_2023", "Ranking_PIBpc_2023", "Ranking_Crescimento_Acumulado"]
    
    float1_cols = [c for c in df.select_dtypes(include="number").columns if c not in int_cols]

    for col in int_cols:
        df[col] = _to_int(df[col])
    for col in float1_cols:
        df[col] = _to_float1(df[col])

    _log("ok", f"Resultado — {len(df)} países | {len(df.columns)} colunas")
    return df


# ========================= 4. TRANSFORMAÇÃO - REGIÕES =========================

def transformar_regioes(df):
    _section(4, "TRANSFORMAÇÃO — REGIOES")
    df = df.copy()

    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].str.strip()

    int_cols = ["Ranking_PIB_2023", "No_Países"]
    float1_cols = [c for c in df.select_dtypes(include="number").columns if c not in int_cols]

    for col in int_cols:
        df[col] = _to_int(df[col])
    for col in float1_cols:
        df[col] = _to_float1(df[col])

    _log("ok", f"Resultado — {len(df)} regiões | {len(df.columns)} colunas")
    return df


# ========================= 5. SÉRIE TEMPORAL =========================

def construir_serie(paises):
    _section(5, "CONSTRUÇÃO DA SÉRIE TEMPORAL")

    pib, pibpc, cresc = _col_map(paises)
    anos = sorted(pib.keys())
    rows = []

    for _, p in paises.iterrows():
        base = p[pib[2000]] if pd.notna(p[pib.get(2000, None)]) and p[pib.get(2000, None)] > 0 else None

        for ano in anos:
            v_pib = _round1(p[pib[ano]])

            # PIB per capita
            v_pibpc = None
            if ano in pibpc and pd.notna(p[pibpc[ano]]):
                v_pibpc = int(round(p[pibpc[ano]]))

            # Crescimento anual
            if ano in cresc and pd.notna(p[cresc[ano]]):
                v_cresc = _round1(p[cresc[ano]])
            elif ano == 2000:
                v_cresc = None  # Não existe crescimento no primeiro ano
            else:
                ano_ant = max(a for a in anos if a < ano)
                v_ant = p[pib[ano_ant]]
                v_cresc = _round1((p[pib[ano]] - v_ant) / v_ant * 100) \
                          if pd.notna(v_ant) and v_ant > 0 and pd.notna(p[pib[ano]]) else None

            # Crescimento vs 2000
            v_vs2000 = _round1((p[pib[ano]] - base) / base * 100) \
                       if base and pd.notna(p[pib[ano]]) else None

            rows.append({
                "País":                  p["País"].strip(),
                "Código_ISO3":           p["Código_ISO3"].strip(),
                "Região":                p["Região"].strip(),
                "Ano":                   int(ano),
                "Era_Económica":         ERAS[ano][0],
                "Ordem_Era":             ERAS[ano][1],
                "PIB_USD_Bilhões":       v_pib,
                "PIB_por_Habitante_USD": v_pibpc,
                "Crescimento_PIB_%":     v_cresc,
                "Crescimento_vs_2000_%": v_vs2000,
                "Cor_Linha":             "Angola" if p["Código_ISO3"].strip() == "AGO" else "Outros",
            })

    df = pd.DataFrame(rows)

    # Tipagem final
    df["Ano"]                     = df["Ano"].astype(int)
    df["Ordem_Era"]               = df["Ordem_Era"].astype(int)
    df["PIB_por_Habitante_USD"]   = _to_int(df["PIB_por_Habitante_USD"])
    df["PIB_USD_Bilhões"]         = _to_float1(df["PIB_USD_Bilhões"])
    df["Crescimento_PIB_%"]       = _to_float1(df["Crescimento_PIB_%"])
    df["Crescimento_vs_2000_%"]   = _to_float1(df["Crescimento_vs_2000_%"])

    n_p = df["Código_ISO3"].nunique()
    n_a = df["Ano"].nunique()
    diff = abs(round(df[df["Ano"]==2023]["PIB_USD_Bilhões"].sum(), 1) - 
               round(paises["PIB_2023_USD_Bilhões"].sum(), 1))

    _log("ok",  f"Resultado — {len(df)} linhas | {n_p} países | {n_a} anos")
    _log("err" if df["Crescimento_PIB_%"].isna().sum() else "ok",
         f"Nulos em Crescimento_PIB_%: {df['Crescimento_PIB_%'].isna().sum()}" if df["Crescimento_PIB_%"].isna().sum() else "Sem nulos em Crescimento_PIB_%")
    _log("err" if diff > 0.5 else "ok",
         f"PIB 2023: série=${round(df[df['Ano']==2023]['PIB_USD_Bilhões'].sum(),1)}B vs paises=${round(paises['PIB_2023_USD_Bilhões'].sum(),1)}B")

    return df


# ========================= 6. VALIDAÇÃO FINAL =========================

def validar_final(paises, serie):
    _section(6, "VALIDAÇÃO FINAL")

    for col in ["Tooltip_Mapa", "Cor_Destaque", "Top10_PIB_2023", "Grupo_Crescimento"]:
        status = "presente" if col in paises.columns else "AUSENTE"
        _log("ok" if col in paises.columns else "err", f"Coluna '{col}' {status}")

    ausentes = set(paises["Código_ISO3"]) - set(serie["Código_ISO3"])
    _log("err" if ausentes else "ok",
         f"Série: {serie['Código_ISO3'].nunique()}/30 países" + (f" | ausentes: {sorted(ausentes)}" if ausentes else ""))

    _log("err" if (serie["Ordem_Era"] == 0).sum() else "ok", "Todas as eras mapeadas")

    angola = paises[paises["Código_ISO3"] == "AGO"].iloc[0]
    _log("ok", f"Angola — PIB: ${angola['PIB_2023_USD_Bilhões']}B | "
               f"Ranking PIB: #{angola['Ranking_PIB_2023']} | "
               f"Ranking PIBpc: #{angola['Ranking_PIBpc_2023']} | "
               f"Crescimento: +{angola['Crescimento_Acumulado_2000_2023_%']}%")
    return angola


# ========================= 7. EXPORTAÇÃO =========================

def exportar(paises, regioes, serie):
    _section(7, "EXPORTAÇÃO")
    os.makedirs(OUT_DIR, exist_ok=True)
    
    for nome, df in [("paises.csv", paises), 
                     ("regioes.csv", regioes), 
                     ("serie_temporal.csv", serie)]:
        path = os.path.join(OUT_DIR, nome)
        df.to_csv(path, index=False, encoding="utf-8-sig")
        _log("ok", f"{nome} — {len(df)} linhas | {len(df.columns)} colunas  →  {path}")


# ========================= RELATÓRIO FINAL =========================

def relatorio(paises, serie, angola):
    cresc = (paises["PIB_2023_USD_Bilhões"].sum() - paises["PIB_2000_USD_Bilhões"].sum()) \
          / paises["PIB_2000_USD_Bilhões"].sum() * 100

    print("\n" + "="*60)
    print("RELATÓRIO FINAL")
    print("="*60)
    print(f"  PIB Total África 2023       : ${paises['PIB_2023_USD_Bilhões'].sum():.1f}B")
    print(f"  PIB Total África 2000       : ${paises['PIB_2000_USD_Bilhões'].sum():.1f}B")
    print(f"  Crescimento Continente      : +{cresc:.1f}%")
    print(f"  Países                      : {paises['Código_ISO3'].nunique()}")
    print(f"  Maior economia              : {paises.nlargest(1,'PIB_2023_USD_Bilhões')['País'].values[0]}")
    print(f"  Maior crescimento           : {paises.nlargest(1,'Crescimento_Acumulado_2000_2023_%')['País'].values[0]}")
    print(f"  Maior PIB per capita        : {paises.nlargest(1,'PIB_por_Habitante_2023_USD')['País'].values[0]}")
    print(f"  {'─'*55}")
    print(f"  Angola PIB 2023             : ${angola['PIB_2023_USD_Bilhões']:.1f}B")
    print(f"  Angola Ranking PIB          : #{int(angola['Ranking_PIB_2023'])}")
    print(f"  Angola Ranking PIBpc        : #{int(angola['Ranking_PIBpc_2023'])}")
    print(f"  Angola Crescimento Acum.    : +{angola['Crescimento_Acumulado_2000_2023_%']:.1f}%")
    print(f"  Angola Ranking Crescimento  : #{int(angola['Ranking_Crescimento_Acumulado'])}")
    print(f"  {'─'*55}")
    print(f"  Série temporal              : {serie['Código_ISO3'].nunique()} países × {serie['Ano'].nunique()} anos = {len(serie)} linhas")
    print("="*60)

    if _erros:
        print(f"  ATENÇÃO — {len(_erros)} ERRO(S):")
        for e in _erros:
            print(f"    ✗ {e}")
    else:
        print("  PIPELINE CONCLUÍDA COM SUCESSO!")
    print("="*60)


# ========================= MAIN =========================

def main():
    print("="*60)
    print("PIPELINE — ÁFRICA PIB 2000-2023")
    print("="*60)

    paises_raw, regioes_raw = extrair()
    validar(paises_raw, regioes_raw)

    paises  = transformar_paises(paises_raw)
    regioes = transformar_regioes(regioes_raw)
    serie   = construir_serie(paises_raw)

    angola = validar_final(paises, serie)
    exportar(paises, regioes, serie)
    relatorio(paises, serie, angola)


if __name__ == "__main__":
    main()