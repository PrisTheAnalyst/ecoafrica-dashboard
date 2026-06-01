ANGOLA   = "#E8720A"
ANGOLA_D = "#C0390A"
BLUE     = "#3A3A6E"
BLUE_L   = "#6B8CCC"
GREEN    = "#27AE60"
GREEN_L  = "#52D68A"
RED      = "#C0392B"
GOLD     = "#D4A017"
WHITE    = "#F5F0E8"
MUTED    = "#8A8090"
MUTED_L  = "#B0A8B0"
BG       = "#080810"
CARD     = "#0F0F1A"
CARD_L   = "#16162A"
BORDER   = "#1E1E32"
GRID     = "#14142A"

PEERS    = ["AGO", "NGA", "ZAF", "ETH"]
PEERS_N  = {"AGO":"Angola","NGA":"Nigéria","ZAF":"África do Sul","ETH":"Etiópia"}
PEERS_C  = {"Angola":ANGOLA,"Nigéria":BLUE_L,"África do Sul":GREEN,"Etiópia":GOLD}
TOP5_ISO = ["AGO","NGA","ZAF","EGY","DZA","ETH"]

CORES_LINHA = {
    "AGO":ANGOLA,"NGA":BLUE_L,"ZAF":GREEN,
    "ETH":GOLD,"EGY":"#8A4FC8","MAR":"#4ABCB8","KEN":"#D45050",
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [data-testid="stApp"] {
    background: #080810;
    font-family: 'Inter', sans-serif;
}
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display:none !important; }
.block-container { padding:1.5rem 2rem 3rem !important; max-width:1440px !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0A0A16 !important;
    border-right: 1px solid #1E1E32 !important;
    min-width:220px !important; max-width:220px !important;
}
[data-testid="stSidebarContent"] { padding:2rem 1.3rem !important; }
.nav-brand { color:#F5F0E8; font-size:17px; font-weight:800; letter-spacing:.01em; }
.nav-version { color:#E8720A; font-size:10px; font-weight:600;
               letter-spacing:.12em; text-transform:uppercase;
               background:#1E0A00; padding:2px 7px; border-radius:4px;
               display:inline-block; margin-top:4px; }
.nav-sub   { color:#8A8090; font-size:10px; letter-spacing:.1em;
             text-transform:uppercase; padding-bottom:1.2rem;
             border-bottom:1px solid #1E1E32; margin-bottom:1.4rem; }
.nav-label { color:#8A8090; font-size:10px; font-weight:600;
             letter-spacing:.12em; text-transform:uppercase; margin-bottom:.5rem; }
.nav-footer{ color:#8A8090; font-size:10px; line-height:2;
             border-top:1px solid #1E1E32; padding-top:1.2rem; margin-top:1.5rem; }

/* ── KPI cards ── */
.kpi {
    background: linear-gradient(135deg, #0F0F1A 0%, #13132A 100%);
    border: 1px solid #1E1E32;
    border-radius:14px; padding:1.1rem 1.3rem; text-align:center;
    transition: border-color .2s, transform .15s;
    position: relative; overflow: hidden;
}
.kpi::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg, transparent, #E8720A33, transparent);
}
.kpi:hover { border-color:#E8720A55; transform:translateY(-1px); }
.kpi-label { color:#8A8090; font-size:10px; font-weight:600;
             text-transform:uppercase; letter-spacing:.1em; margin-bottom:8px; }
.kpi-value { color:#F5F0E8; font-size:22px; font-weight:700; line-height:1.1;
             font-variant-numeric:tabular-nums; }
.kpi-sub   { color:#8A8090; font-size:11px; margin-top:5px; }
.kpi-pos   { color:#4ADE80; font-size:22px; font-weight:700; }
.kpi-neg   { color:#F87171; font-size:22px; font-weight:700; }
.kpi-warn  { color:#E8720A; font-size:22px; font-weight:700; }

/* ── Insight box ── */
.insight {
    background: linear-gradient(135deg, #0F1A0F, #131A13);
    border: 1px solid #1E321E;
    border-left: 3px solid #27AE60;
    border-radius: 0 10px 10px 0;
    padding: .7rem 1.1rem;
    font-size: 12px; color: #B0C8B0; line-height: 1.65;
    margin-bottom: 1rem;
}
.insight strong { color: #52D68A; }
.insight.angola {
    background: linear-gradient(135deg, #1A0F08, #1A1308);
    border-color: #2A1A08; border-left-color: #E8720A;
    color: #C8B890;
}
.insight.angola strong { color: #E8720A; }
.insight.warn {
    background: linear-gradient(135deg, #1A0808, #1A1308);
    border-color: #2A0808; border-left-color: #F87171;
    color: #C89090;
}
.insight.warn strong { color: #F87171; }

/* ── Section heading ── */
.sec {
    display:flex; align-items:center; gap:10px;
    margin: 1.8rem 0 .8rem;
}
.sec-line { width:3px; height:18px; background:#E8720A; border-radius:2px; flex-shrink:0; }
.sec-text { color:#F5F0E8; font-size:12px; font-weight:700;
            text-transform:uppercase; letter-spacing:.1em; }
.sec-badge { color:#8A8090; font-size:10px; background:#1E1E32;
             padding:2px 8px; border-radius:4px; margin-left:auto; }

/* ── Page header ── */
.page-title { color:#F5F0E8; font-size:24px; font-weight:800; margin-bottom:3px; letter-spacing:-.01em; }
.page-desc  { color:#8A8090; font-size:13px; margin-bottom:1.4rem; line-height:1.6; }

/* ── Metric delta inline ── */
.delta-pos { color:#4ADE80; font-size:11px; font-weight:600; }
.delta-neg { color:#F87171; font-size:11px; font-weight:600; }

/* ── Filter label ── */
.filter-label { color:#8A8090; font-size:10px; font-weight:600;
                letter-spacing:.08em; text-transform:uppercase; margin-bottom:4px; }

hr { border-color:#1E1E32; margin:.8rem 0; }
</style>
"""
