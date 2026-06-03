# EcoÁfrica: Dashboard de PIB Africano 2000–2023

Análise económica interactiva de 30 países africanos ao longo de 23 anos.
Construído com Python, Streamlit e Plotly. Dados: World Bank Open Data.

**Demo ao vivo:** [ecoafrica.streamlit.app](https://ecoafrica.streamlit.app/)

---

## O que é

EcoÁfrica é um dashboard analítico que explora a evolução do PIB africano entre 2000 e 2023,
cobrindo 30 países, 7 eras económicas e indicadores de finanças públicas.

O projecto tem foco especial em **Angola** crescimento acumulado de +831%,
posição #8 em África, e a tensão entre crescimento macroeconómico e bem-estar por habitante.

---

## Abas

| Aba         | Conteúdo                                                         |
| ----------- | ----------------------------------------------------------------- |
| Capa        | Visão geral e gráfico de entrada                                |
| África     | Mapa coroplético, rankings, evolução por era e região         |
| Angola      | Peers, quadrantes PIBpc vs crescimento, tabela comparativa, radar |
| Finanças   | Dívida pública, inflação, IDE e mapa de risco fiscal          |
| Dicionário | Glossário de variáveis, eras económicas e KPIs de referência  |
| Extras      | Changelog, roadmap e limitações do dataset                      |

---

## Estrutura do projecto

```
africa_dashboard/
├── app.py                  # Entrada principal: Streamlit
├── _africa.py              # Dashboard África
├── _angola.py              # Dashboard Angola
├── financas.py             # Dashboard Finanças Públicas
├── dicionario.py           # Dicionário de Dados
├── extras.py               # Changelog e Roadmap
├── components.py           # Componentes reutilizáveis (kpi, insight, section)
├── config.py               # Cores, constantes e CSS global
├── data_loader.py          # Carregamento e métricas derivadas
├── data/
│   ├── paises.csv
│   ├── regioes.csv
│   └── serie_temporal.csv
├── assets/
│   ├── mumuila.png
│   └── fundo.png
└── requirements.txt
```

---

## Instalação local

**Pré-requisitos:** Python 3.10+

```bash
git clone https://github.com/SEU_USERNAME/ecoafrica-dashboard.git
cd ecoafrica-dashboard/africa_dashboard
pip install -r requirements.txt
streamlit run app.py
```

Acede em `http://localhost:8501`.

---

## Deploy no Streamlit Cloud (link público gratuito)

1. Faz fork ou push deste repositório para o teu GitHub
2. Acede a [share.streamlit.io](https://share.streamlit.io/) e faz login com GitHub
3. Clica em **New app**
4. Preenche:
   * **Repository:** `SEU_USERNAME/ecoafrica-dashboard`
   * **Branch:** `main`
   * **Main file path:** `africa_dashboard/app.py`
5. Clica em **Deploy**

Em 2–3 minutos tens um link público do tipo `https://ecoafrica.streamlit.app`.
Qualquer push para `main` faz re-deploy automático.

---

## Stack técnica

* **Python 3.11**
* **Streamlit** interface e navegação
* **Plotly**  gráficos interactivos (choropleth, scatter, bar, radar, lines)
* **Pandas**  transformação e filtragem de dados
* **World Bank Open Data**  fonte dos dados económicos

---

## Dados

Os ficheiros CSV em `data/` foram compilados a partir do World Bank Open Data.
O ficheiro Excel original com dicionário e KPIs está em `africa_pib_completo_2000_2023_final.xlsx`.

Cobertura: 30 países africanos · 2000, 2006, 2009, 2010, 2014, 2015, 2019, 2020, 2021, 2022, 2023.

---

## Autor

**Margarida**Data Analist & Social Project Manager

Luanda, Angola · [LinkedIn](www.linkedin.com/in/margarida-baltazar) · [GitHub](https://github.com/PrisTheAnalyst)


*Projecto académico e de portfólio. Dados para fins analíticos e educativos.*
