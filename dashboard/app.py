"""
Dashboard ERP Consulting Performance — konteks PT Beone Optima Solusi.
Jalankan:  streamlit run dashboard/app.py

Dataset 100% sintetis — bukan data riil perusahaan.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from scipy import stats
from sklearn.model_selection import (StratifiedKFold, cross_val_predict,
                                     cross_val_score)

st.set_page_config(page_title="BeOne ERP Analytics", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")

# ---- Clean minimal palette: satu aksen teal + netral ----
# Warna hanya dipakai saat bermakna (merah=risiko, hijau=positif, amber=perhatian)
C_BLUE, C_CYAN, C_TEAL = "#0F766E", "#0E7490", "#0F766E"
C_GREEN, C_AMBER, C_ORANGE = "#16A34A", "#D97706", "#B45309"
C_PINK, C_PURPLE, C_RED = "#B05A78", "#1E40AF", "#DC2626"
PALETTE = ["#0F766E", "#94A3B8", "#64748B", "#475569",
           "#1E40AF", "#A5B4C5", "#0E7490", "#CBD5E1"]
PRODUK_COLOR = {"SAP Business One": "#1E40AF", "SAP S/4HANA GROW": "#0E7490",
                "Add-on & Integrasi": "#64748B", "Business Insight": "#B05A78",
                "TSplus": "#475569", "Training/Xpertise Academy": "#B45309"}

st.markdown("""
<style>
    .block-container {padding-top:1.2rem;padding-bottom:2.5rem;max-width:1320px;}
    [data-testid="stAppViewContainer"] {background:#F5F7FB;}
    [data-testid="stSidebar"] {background:#FFFFFF;border-right:1px solid #E8ECF2;}
    [data-testid="stSidebar"] * {color:#334155 !important;}
    [data-testid="stSidebar"] .stMultiSelect label {font-weight:600;}

    /* ---------- Hero: soft gradient + chips ---------- */
    .hero {position:relative;overflow:hidden;
        background:linear-gradient(115deg,#FFFFFF 42%,#EBFBF7 100%);
        border:1px solid #E6EAF2;border-radius:18px;
        padding:1.5rem 1.7rem 1.35rem;margin:0 0 1.35rem;
        box-shadow:0 4px 18px rgba(15,23,42,.05);}
    .hero::after {content:"";position:absolute;right:-70px;top:-90px;
        width:260px;height:260px;border-radius:50%;
        background:radial-gradient(circle,rgba(15,118,110,.14) 0%,transparent 70%);}
    .hero .eyebrow {font-size:.7rem;font-weight:800;letter-spacing:1.6px;
        text-transform:uppercase;color:#0F766E;margin-bottom:.35rem;}
    .hero h1 {margin:0;font-size:1.6rem;font-weight:800;
        letter-spacing:-.3px;color:#0F172A;}
    .hero p {margin:.45rem 0 .75rem;font-size:.92rem;color:#5B6B83;
        max-width:60rem;}
    .hero .chip {display:inline-block;font-size:.71rem;font-weight:600;
        background:rgba(255,255,255,.8);border:1px solid #E2E8F0;
        border-radius:999px;padding:.22rem .7rem;margin:0 .4rem .1rem 0;
        color:#475569;}
    .hero .chip b {color:#0F172A;}

    /* ---------- KPI cards ---------- */
    .kpi-grid {display:grid;gap:.9rem;margin-bottom:.5rem;
        grid-template-columns:repeat(5,1fr);}
    .kpi {background:#FFFFFF;border:1px solid #E8ECF2;border-radius:14px;
        padding:.95rem 1.05rem .85rem;min-width:0;position:relative;
        overflow:hidden;box-shadow:0 1px 3px rgba(15,23,42,.05);
        transition:transform .16s ease,box-shadow .16s ease;}
    .kpi:hover {transform:translateY(-3px);
        box-shadow:0 8px 20px rgba(15,23,42,.09);}
    .kpi::before {content:"";position:absolute;top:0;left:0;right:0;
        height:3px;background:linear-gradient(90deg,#0F766E,#0F766E55);}
    .kpi .top {display:flex;align-items:center;gap:.45rem;}
    .kpi .icon {font-size:.95rem;}
    .kpi .label {font-size:.72rem;font-weight:700;color:#64748B;
        text-transform:uppercase;letter-spacing:.5px;}
    .kpi .value {font-size:1.7rem;font-weight:800;color:#0F172A;
        line-height:1.15;margin:.3rem 0 .1rem;word-break:break-word;}
    .kpi .sub {font-size:.76rem;color:#94A3B8;}

    /* ---------- Section pill ---------- */
    .sec-pill {display:inline-flex;align-items:center;gap:.45rem;
        font-size:.78rem;font-weight:800;letter-spacing:.6px;
        text-transform:uppercase;color:#475569;
        background:#FFFFFF;border:1px solid #E8ECF2;
        padding:.32rem .85rem;border-radius:999px;margin:.8rem 0 .45rem;
        box-shadow:0 1px 2px rgba(15,23,42,.04);}
    .sec-pill .dot {width:8px;height:8px;border-radius:50%;
        background:#0F766E;box-shadow:0 0 0 3px rgba(15,118,110,.15);}

    /* ---------- Insight tinted ---------- */
    .insight {border-radius:12px;padding:.85rem 1.05rem;font-size:.88rem;
        margin:.65rem 0;border:1px solid;line-height:1.55;}
    .insight.blue {background:#EFF6FF;border-color:#BFDBFE;color:#1E3A8A;}
    .insight.green {background:#F0FDF4;border-color:#BBF7D0;color:#14532D;}
    .insight.amber {background:#FFFBEB;border-color:#FDE68A;color:#78350F;}
    .insight.red {background:#FEF2F2;border-color:#FECACA;color:#7F1D1D;}

    /* ---------- Tabs: segmented control ---------- */
    .stTabs [data-baseweb="tab-list"] {gap:.35rem;border-bottom:none;
        background:#FFFFFF;padding:.35rem;border-radius:14px;
        border:1px solid #E8ECF2;width:fit-content;max-width:100%;
        box-shadow:0 1px 3px rgba(15,23,42,.04);}
    .stTabs [data-baseweb="tab"] {border-radius:10px;padding:.5rem 1rem;
        font-weight:600;font-size:.9rem;color:#64748B;border:none;}
    .stTabs [aria-selected="true"] {background:#0F766E !important;
        color:#FFFFFF !important;}
    .stTabs [data-baseweb="tab-highlight"] {display:none;}

    [data-testid="stExpander"] {background:#FFF;border-radius:12px;
        border:1px solid #E8ECF2;}
    [data-testid="stDataFrame"] {border-radius:12px;overflow:hidden;
        border:1px solid #E8ECF2;background:#FFFFFF;}
    [data-testid="stMetric"] {background:#FFFFFF;border:1px solid #E8ECF2;
        border-radius:12px;padding:.6rem .9rem;}
    div[data-testid="stSelectbox"] label {font-weight:600;}

    /* ---------- Footer ---------- */
    .footer {margin-top:2.2rem;padding-top:1rem;
        border-top:1px solid #E6EAF2;font-size:.75rem;color:#94A3B8;
        display:flex;justify-content:space-between;flex-wrap:wrap;gap:.4rem;}
    .footer b {color:#64748B;}

    /* ---------- Responsive ---------- */
    @media (max-width:1000px) {
        .kpi-grid {grid-template-columns:repeat(3,1fr);}
        .stTabs [data-baseweb="tab"] {padding:.4rem .65rem;font-size:.82rem;}
    }
    @media (max-width:640px) {
        .block-container {padding-left:.8rem;padding-right:.8rem;}
        .kpi-grid {grid-template-columns:repeat(2,1fr);gap:.6rem;}
        .kpi {padding:.8rem .8rem .7rem;}
        .kpi .value {font-size:1.3rem;}
        .hero {padding:1.1rem 1.15rem;}
        .hero h1 {font-size:1.25rem;}
        .hero p {font-size:.85rem;}
        .hero .chip {font-size:.66rem;padding:.18rem .55rem;}
        .sec-pill {font-size:.7rem;}
        .insight {font-size:.82rem;padding:.7rem .8rem;}
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------ #
@st.cache_data
def load_data():
    return (pd.read_csv("data/raw/leads.csv"),
            pd.read_csv("data/raw/opportunities.csv"),
            pd.read_csv("data/raw/proyek.csv"),
            pd.read_csv("data/raw/tiket.csv"),
            pd.read_csv("data/raw/konsultan.csv"))

leads, opp, proyek, tiket, konsultan = load_data()

def titik(x):
    return f"{x:,.0f}".replace(",", ".")

def miliar(x):
    return f"Rp{x/1000:.1f} M".replace(".", ",")

BASE_LAYOUT = dict(
    font=dict(family="Inter, Segoe UI, sans-serif", size=13, color="#1F2937"),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=46, b=10),
    title=dict(font=dict(size=15, color="#1F2937")),
    colorway=PALETTE)

def polish(fig, **kw):
    fig.update_layout(**{**BASE_LAYOUT, **kw})
    fig.update_xaxes(showgrid=False, zeroline=False, automargin=True)
    fig.update_yaxes(gridcolor="#EEF2F6", zeroline=False, automargin=True,
                     title_standoff=10)
    fig.update_traces(cliponaxis=False, selector=dict(type="bar"))
    fig.update_layout(uniformtext_minsize=9, uniformtext_mode="hide")
    return fig

def chart(fig):
    st.plotly_chart(fig, width="stretch")

def table(df, **kw):
    st.dataframe(df, width="stretch", hide_index=True, **kw)

def insight_box(text, tone="blue"):
    st.markdown(f'<div class="insight {tone}">💡 {text}</div>',
                unsafe_allow_html=True)

def sec(icon, label, color=None):
    st.markdown(
        f'<div class="sec-pill"><span class="dot"></span>{icon} {label}</div>',
        unsafe_allow_html=True)

def penjelasan(judul, isi_md):
    with st.expander(f"📖 {judul}"):
        st.markdown(isi_md)

# ------------------------------------------------------------------ #
#  Sidebar filters                                                    #
# ------------------------------------------------------------------ #
st.sidebar.markdown("## 🎛️ Filter Data")
st.sidebar.caption("Semua visual mengikuti filter ini")

th_list = sorted(leads["tahun"].unique())
th_pilih = st.sidebar.multiselect("Tahun Lead", th_list, default=th_list)
ind_pilih = st.sidebar.multiselect(
    "Industri Klien", sorted(leads["industri"].unique()),
    default=sorted(leads["industri"].unique()))
prod_pilih = st.sidebar.multiselect(
    "Produk", sorted(opp["produk"].unique()),
    default=sorted(opp["produk"].unique()))

st.sidebar.divider()
st.sidebar.caption("📊 Dataset sintetis · konteks publik PT Beone Optima Solusi")

lead_id_ok = set(leads.loc[leads["tahun"].isin(th_pilih)
                           & leads["industri"].isin(ind_pilih), "id_lead"])
ld = leads[leads["id_lead"].isin(lead_id_ok)]
op = opp[opp["id_lead"].isin(lead_id_ok) & opp["produk"].isin(prod_pilih)]
pj = proyek[proyek["id_opportunity"].isin(set(op["id_opportunity"]))]
tk = tiket[tiket["id_proyek"].isin(set(pj["id_proyek"]))]

if ld.empty or op.empty:
    st.warning("Filter menghasilkan data kosong — pilih minimal satu tahun, "
               "industri, dan produk di sidebar.")
    st.stop()

# ------------------------------------------------------------------ #
#  Hero + KPI                                                         #
# ------------------------------------------------------------------ #
st.markdown("""
<div class="hero">
  <div class="eyebrow">Portfolio Project · B2B Consulting Analytics</div>
  <h1>📊 ERP Consulting Performance</h1>
  <p>Analisis end-to-end funnel & delivery konsultan ERP — pipeline B2B,
     win rate per channel, on-time go-live, SLA support, dan delay
     predictor. Konteks PT Beone Optima Solusi (SAP Gold Partner).</p>
  <span class="chip"><b>2.900</b> leads</span>
  <span class="chip"><b>3.397</b> tiket support</span>
  <span class="chip">6 lini produk</span>
  <span class="chip">📅 2019–2025</span>
  <span class="chip">Dataset sintetis</span>
</div>
""", unsafe_allow_html=True)

n_lead, n_opp = len(ld), len(op)
n_won = (op["hasil"] == "Won").sum()
pipeline_jt = op["nilai_deal_jt"].sum()
won_jt = op.loc[op["hasil"] == "Won", "nilai_deal_jt"].sum()
pj_done = pj.dropna(subset=["tanggal_golive"])
on_time = (100 * (pj_done["status_proyek"] == "Go-live Tepat Waktu").mean()
           if len(pj_done) else 0)
sla_pct = 100 * tk["sla_tercapai"].mean() if len(tk) else 0

kpis = [
    ("📥", "Total Leads", titik(n_lead), f"{len(th_pilih)} tahun"),
    ("💼", "Pipeline Value", miliar(pipeline_jt),
     f"{titik(n_opp)} opportunity"),
    ("🎯", "Win Rate", f"{100*n_won/max(n_opp,1):.1f}%".replace(".", ","),
     f"{miliar(won_jt)} revenue won"),
    ("🚀", "On-time Go-live", f"{on_time:.0f}%",
     f"{len(pj_done)} proyek selesai"),
    ("🛟", "SLA Support", f"{sla_pct:.0f}%", f"{titik(len(tk))} tiket"),
]
kpi_html = '<div class="kpi-grid">'
for icon, label, val, sub in kpis:
    kpi_html += (f'<div class="kpi"><div class="top">'
                 f'<span class="icon">{icon}</span>'
                 f'<span class="label">{label}</span></div>'
                 f'<div class="value">{val}</div>'
                 f'<div class="sub">{sub}</div></div>')
st.markdown(kpi_html + "</div>", unsafe_allow_html=True)

st.write("")
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["💼 Pipeline & Revenue", "🚀 Delivery Proyek", "🛟 Support & SLA",
     "👥 Tim Konsultan", "🔮 Prediktif & Eksplorasi"])

# ------------------------------------------------------------------ #
#  TAB 1 — Pipeline & Revenue                                         #
# ------------------------------------------------------------------ #
with tab1:
    c1, c2 = st.columns([3, 2], gap="large")

    with c1:
        sec("📈", "Pertumbuhan funnel per tahun", C_BLUE)
        fun = (ld.groupby("tahun")["id_lead"].count().rename("Leads")
               .to_frame().join(
            op.join(ld.set_index("id_lead")["tahun"], on="id_lead")
              .groupby("tahun")["id_opportunity"].count().rename("Opportunity"))
               .join(
            op[op.hasil == "Won"]
              .join(ld.set_index("id_lead")["tahun"], on="id_lead")
              .groupby("tahun")["id_opportunity"].count().rename("Won"))
               .fillna(0).reset_index())
        fig = go.Figure()
        for col_, color in [("Leads", C_BLUE), ("Opportunity", C_TEAL),
                            ("Won", C_GREEN)]:
            fig.add_trace(go.Scatter(
                x=fun["tahun"], y=fun[col_], name=col_, mode="lines+markers",
                line=dict(width=3.5, color=color), marker=dict(size=9),
                fill="tozeroy" if col_ == "Leads" else None,
                fillcolor="rgba(59,130,246,.10)"))
        polish(fig, legend=dict(orientation="h", y=1.14))
        chart(fig)

        sec("💰", "Revenue won per tahun (Rp jt)", C_GREEN)
        rev = (op[op.hasil == "Won"]
               .join(ld.set_index("id_lead")["tahun"], on="id_lead")
               .groupby(["tahun", "produk"])["nilai_deal_jt"].sum()
               .reset_index())
        fig = px.bar(rev, x="tahun", y="nilai_deal_jt", color="produk",
                     color_discrete_map=PRODUK_COLOR,
                     labels={"nilai_deal_jt": "Revenue (Rp jt)", "tahun": "",
                             "produk": ""})
        polish(fig, legend=dict(orientation="h", y=1.14))
        chart(fig)

    with c2:
        sec("🧲", "Funnel konversi B2B", C_PURPLE)
        n_pj = len(pj)
        fig = go.Figure(go.Funnel(
            y=["Leads", "Opportunity", "Won", "Proyek Jalan"],
            x=[n_lead, n_opp, n_won, n_pj],
            textinfo="value+percent initial",
            marker=dict(color=["#134E4A", "#0F766E", "#14B8A6", "#99F6E4"]),
            connector=dict(line=dict(color="#E5E7EB", width=2))))
        polish(fig)
        chart(fig)

        sec("🎯", "Win rate per sumber lead", C_TEAL)
        ws = (op.join(ld.set_index("id_lead")["sumber"], on="id_lead")
              .groupby("sumber")["hasil"]
              .apply(lambda s: 100 * (s == "Won").mean())
              .sort_values().reset_index(name="wr"))
        fig = px.bar(ws, x="wr", y="sumber", orientation="h",
                     color="sumber", color_discrete_sequence=PALETTE,
                     text=ws["wr"].map("{:.0f}%".format),
                     labels={"wr": "", "sumber": ""})
        fig.update_traces(textposition="outside")
        polish(fig, showlegend=False, xaxis_title="Win rate %")
        chart(fig)

    sec("🏢", "Revenue won per entitas (struktur grup)", C_PURPLE)
    ent = (op[op.hasil == "Won"]
           .join(ld.set_index("id_lead")["tahun"], on="id_lead")
           .groupby(["tahun", "entitas"])["nilai_deal_jt"].sum()
           .reset_index())
    fig = px.bar(ent, x="tahun", y="nilai_deal_jt", color="entitas",
                 barmode="stack",
                 color_discrete_map={"BeOne HQ": "#0F766E",
                                     "PT CORE (sister)": "#B05A78"},
                 labels={"nilai_deal_jt": "Revenue (Rp jt)", "tahun": "",
                         "entitas": ""})
    polish(fig, legend=dict(orientation="h", y=1.14))
    chart(fig)
    st.caption("PT CORE = sister company yang berdiri ~2023 dan mengambil "
               "alih sebagian implementasi SAP B1 sejak 2024.")

    sec("🏭", "Pipeline per industri × produk", C_ORANGE)
    heat = (op.join(ld.set_index("id_lead")["industri"], on="id_lead")
            .groupby(["industri", "produk"])["nilai_deal_jt"].sum()
            .unstack(fill_value=0))
    fig = px.imshow(heat, aspect="auto", color_continuous_scale="Teal",
                    text_auto=True,
                    labels=dict(x="", y="", color="Rp jt"))
    polish(fig)
    chart(fig)

    sec("⏳", "Distribusi sales cycle (hari, deal Won)", C_AMBER)
    sc = op[op.hasil == "Won"]
    fig = px.histogram(sc, x="sales_cycle_hari", color="produk", nbins=40,
                       barmode="overlay", opacity=0.6,
                       color_discrete_map=PRODUK_COLOR,
                       labels={"sales_cycle_hari": "Sales cycle (hari)",
                               "produk": ""})
    polish(fig, legend=dict(orientation="h", y=1.14))
    chart(fig)

    penjelasan("Cara membaca bagian ini", """
**Funnel B2B** menelusuri perjalanan prospek: lead mentah → masuk pipeline
resmi (opportunity) → deal menang (Won) → proyek implementasi jalan.
Drop terbesar biasanya di lead→opportunity (kualifikasi awal) — normal
di bisnis konsultan; yang penting adalah win rate di pipeline.

**Win rate per sumber** menjawab pertanyaan marketing B2B paling penting:
*sumber mana yang menghasilkan deal, bukan cuma lead?* Referral & event
(workshop seperti "Business Hacks") biasanya jauh lebih efektif daripada
telemarketing dingin — lead hangat sudah punya konteks masalah.

**Revenue per produk** menunjukkan bauran portofolio: SAP Business One =
volume (pasar UKM), S/4HANA GROW = deal besar tapi cycle lebih panjang.
Pergeseran bauran ke S/4HANA = naik kelas ke mid-market.

**Sales cycle** = hari dari opportunity dibuat sampai close. ERP punya
cycle panjang (3-6 bulan) karena keputusan melibatkan banyak stakeholder.
S/4HANA lebih panjang lagi — konsekuensi: pipeline forecasting perlu
memperhitungkan lag ini.

⚠️ **Catatan:** semua data sintetis — parameter (win rate, deal size)
adalah asumsi skenario, bukan angka riil perusahaan.
""")

    if len(fun) >= 2:
        _g = 100 * (fun["Leads"].iloc[-1] / fun["Leads"].iloc[0] - 1)
        _wr = ws.iloc[-1]
        insight_box(f"Lead tumbuh <b>{_g:.0f}%</b> dalam periode terpilih — "
                    f"sumber paling efektif: <b>{_wr['sumber']}</b> "
                    f"(win rate {_wr['wr']:.0f}%) vs paling rendah "
                    f"<b>{ws.iloc[0]['sumber']}</b> ({ws.iloc[0]['wr']:.0f}%).", "blue")

# ------------------------------------------------------------------ #
#  TAB 2 — Delivery Proyek                                            #
# ------------------------------------------------------------------ #
with tab2:
    c1, c2 = st.columns(2, gap="large")

    with c1:
        sec("🚀", "Ketepatan go-live per produk", C_GREEN)
        ot = (pj_done.groupby("produk")["status_proyek"]
              .apply(lambda s: 100 * (s == "Go-live Tepat Waktu").mean())
              .reset_index(name="pct"))
        fig = px.bar(ot, x="produk", y="pct", color="produk",
                     color_discrete_map=PRODUK_COLOR,
                     text=ot["pct"].map("{:.0f}%".format),
                     labels={"pct": "% tepat waktu", "produk": ""})
        fig.update_traces(textposition="outside")
        fig.update_yaxes(range=[0, 100])
        polish(fig, showlegend=False)
        chart(fig)

        sec("📉", "Distribusi keterlambatan (hari)", C_RED)
        d = pj_done.assign(delay=pj_done["durasi_aktual_hari"]
                           - pj_done["durasi_target_hari"])
        fig = px.histogram(d, x="delay", color="produk", nbins=50,
                           barmode="overlay", opacity=0.6,
                           color_discrete_map=PRODUK_COLOR,
                           labels={"delay": "Delay (hari; <0 = lebih cepat)",
                                   "produk": ""})
        fig.add_vline(x=0, line_dash="dash", line_color=C_RED)
        polish(fig, legend=dict(orientation="h", y=1.14))
        chart(fig)

    with c2:
        sec("💸", "Deviasi budget per produk", C_AMBER)
        bd = pj_done.assign(dev=100 * (pj_done["aktual_jt"]
                                     - pj_done["budget_jt"]) / pj_done["budget_jt"])
        fig = px.box(bd, x="produk", y="dev", color="produk",
                     color_discrete_map=PRODUK_COLOR, points="outliers",
                     labels={"dev": "Deviasi budget (%)", "produk": ""})
        fig.add_hline(y=0, line_dash="dash", line_color=C_RED)
        polish(fig, showlegend=False)
        chart(fig)

        sec("🧱", "Modul dengan tingkat keterlambatan tertinggi", C_ORANGE)
        md = (pj_done.groupby("modul_utama")["status_proyek"]
              .agg(n="count",
                   late=lambda s: 100 * (s == "Go-live Terlambat").mean())
              .query("n >= 8").sort_values("late").reset_index())
        fig = px.bar(md, x="late", y="modul_utama", orientation="h",
                     color="late", color_continuous_scale="Reds",
                     text=md["late"].map("{:.0f}%".format),
                     labels={"late": "% terlambat", "modul_utama": ""})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        chart(fig)

    penjelasan("Cara membaca bagian ini", """
**On-time go-live** adalah KPI paling kritis di bisnis implementasi ERP —
telat = biaya konsultan membengkak + kepercayaan klien turun. Angka di
dashboard ini berasal dari data sintetis dan **bukan benchmark industri**.

**Distribusi delay** menunjukkan bentuk masalahnya: ekor kanan panjang =
ada proyek "horror story" yang telat ratusan hari (biasanya scope creep
atau data migrasi klien yang berantakan).

**Deviasi budget** = selisih biaya aktual vs budget awal. Overrun >10%
berarti margin proyek tergerus — di bisnis fixed-price, delay langsung
memakan profit.

**Modul terlambat** mengarahkan ke akar masalah: modul integrasi/produksi
sering terlambat karena bergantung pada kesiapan data & proses sisi klien,
bukan murni skill konsultan.
""")

    if len(md):
        _top = md.iloc[-1]
        _prod = (pj_done.groupby("produk")["status_proyek"]
                 .apply(lambda s: 100 * (s == "Go-live Terlambat").mean())
                 .sort_values())
        insight_box(f"Modul paling sering terlambat: <b>{_top['modul_utama']}</b> "
                    f"({_top['late']:.0f}%); produk paling berisiko: "
                    f"<b>{_prod.index[-1]}</b> ({_prod.iloc[-1]:.0f}% terlambat) "
                    f"vs <b>{_prod.index[0]}</b> ({_prod.iloc[0]:.0f}%). "
                    "Kompleksitas & ketergantungan pada data/proses klien "
                    "adalah pendorong yang diasumsikan di model data.", "amber")

# ------------------------------------------------------------------ #
#  TAB 3 — Support & SLA                                              #
# ------------------------------------------------------------------ #
with tab3:
    c1, c2 = st.columns(2, gap="large")

    with c1:
        sec("⏱️", "SLA attainment per prioritas", C_RED)
        sa = (tk.groupby("prioritas")["sla_tercapai"]
              .agg(pct=lambda s: 100 * s.mean(), n="count").reset_index())
        order_p = ["Critical", "High", "Medium", "Low"]
        sa["prioritas"] = pd.Categorical(sa["prioritas"], order_p, True)
        sa = sa.sort_values("prioritas")
        fig = px.bar(sa, x="prioritas", y="pct", color="prioritas",
                     color_discrete_map={"Critical": "#DC2626", "High": "#B45309",
                                         "Medium": "#D97706", "Low": "#64748B"},
                     text=sa["pct"].map("{:.0f}%".format),
                     labels={"pct": "% SLA tercapai", "prioritas": ""})
        fig.update_traces(textposition="outside")
        fig.update_yaxes(range=[0, 105])
        polish(fig, showlegend=False)
        chart(fig)

        sec("🗂️", "Komposisi kategori tiket", C_BLUE)
        kat = tk["kategori"].value_counts()
        fig = go.Figure(go.Pie(labels=kat.index, values=kat.values, hole=0.58,
                               marker=dict(colors=PALETTE),
                               textinfo="label+percent",
                               textposition="outside"))
        polish(fig, showlegend=False)
        chart(fig)

    with c2:
        sec("⚡", "Distribusi waktu resolusi (jam)", C_PURPLE)
        fig = px.box(tk, x="prioritas", y="jam_resolusi", color="prioritas",
                     color_discrete_map={"Critical": "#DC2626", "High": "#B45309",
                                         "Medium": "#D97706", "Low": "#64748B"},
                     labels={"jam_resolusi": "Jam resolusi",
                             "prioritas": ""},
                     category_orders={"prioritas": order_p})
        fig.update_yaxes(type="log")
        polish(fig, showlegend=False)
        chart(fig)

        sec("📊", "Beban tiket per industri", C_TEAL)
        tb = (tk.groupby("industri")
              .agg(tiket=("id_tiket", "count"),
                   proyek=("id_proyek", "nunique"))
              .assign(tpp=lambda d: d["tiket"] / d["proyek"])
              .sort_values("tpp").reset_index())
        fig = px.bar(tb, x="tpp", y="industri", orientation="h",
                     color="tpp", color_continuous_scale="Teal",
                     text=tb["tpp"].map("{:.1f}".format),
                     labels={"tpp": "Tiket per proyek", "industri": ""})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        chart(fig)

    sec("🔗", "Apakah proyek telat menghasilkan lebih banyak tiket?", C_PURPLE)
    pj_done2 = pj.dropna(subset=["tanggal_golive"])
    coh = (tk.groupby("id_proyek").size().rename("n_tiket").reset_index()
           .merge(pj_done2[["id_proyek", "status_proyek"]], on="id_proyek"))
    if len(coh):
        fig = px.box(coh, x="status_proyek", y="n_tiket", color="status_proyek",
                     color_discrete_map={"Go-live Tepat Waktu": "#16A34A",
                                         "Go-live Terlambat": "#DC2626"},
                     points="outliers",
                     labels={"n_tiket": "Tiket pasca go-live",
                             "status_proyek": ""})
        polish(fig, showlegend=False)
        chart(fig)
        _a = coh.loc[coh.status_proyek == "Go-live Terlambat", "n_tiket"]
        _b = coh.loc[coh.status_proyek == "Go-live Tepat Waktu", "n_tiket"]
        if len(_a) > 5 and len(_b) > 5:
            _p = stats.mannwhitneyu(_a, _b).pvalue
            st.caption(
                f"Cohort delivery → support: median tiket **{_a.median():.0f}** "
                f"(terlambat) vs **{_b.median():.0f}** (tepat waktu); "
                f"Mann-Whitney p = {_p:.2g} → "
                + ("perbedaan signifikan secara statistik." if _p < 0.05
                   else "tidak ada bukti perbedaan pada data terfilter."))

    penjelasan("Cara membaca bagian ini", """
**SLA attainment** adalah janji service level ke klien (mis. Critical ≤8 jam).
Prioritas tinggi harus punya attainment TERTINGGI — jika Critical justru
rendah, tim support kebanjiran dan perlu triase ulang.

**Tiket per proyek** adalah proxy kualitas implementasi: proyek yang
go-live-nya mulus menghasilkan sedikit tiket. Industri dengan rasio
tinggi = implementasi lebih kompleks (manufaktur dengan BOM/produksi
wajar lebih tinggi daripada retail sederhana).

**Skala log di boxplot** dipakai karena resolusi punya ekor panjang —
beberapa tiket integrasi bisa memakan ratusan jam.

**Kategori "How-to/Training"** yang dominan adalah sinyal klasik: klien
belum terlatih optimal saat handover — peluang upselling paket training.
""")

    insight_box("Dominasi tiket <b>How-to/Training</b> = peluang bisnis: "
                "penawaran paket training & knowledge base mandiri bisa menekan "
                "volume tiket sekaligus jadi recurring revenue.", "green")

# ------------------------------------------------------------------ #
#  TAB 4 — Tim Konsultan                                              #
# ------------------------------------------------------------------ #
with tab4:
    c1, c2 = st.columns([3, 2], gap="large")

    with c1:
        sec("👥", "Beban & ketepatan per konsultan", C_BLUE)
        perf = (pj_done.groupby("id_konsultan")
                .agg(proyek=("id_proyek", "count"),
                     on_time=("status_proyek",
                              lambda s: 100 * (s == "Go-live Tepat Waktu").mean()),
                     dev=("aktual_jt", "sum"), budget=("budget_jt", "sum"))
                .join(konsultan.set_index("id_konsultan"), on="id_konsultan")
                .reset_index())
        perf["dev_pct"] = 100 * (perf["dev"] - perf["budget"]) / perf["budget"]
        fig = px.scatter(perf, x="proyek", y="on_time", size="proyek",
                         color="level", hover_name="id_konsultan",
                         color_discrete_map={"Senior": "#1E40AF", "Mid": "#0F766E",
                                             "Junior": "#94A3B8"},
                         labels={"proyek": "Proyek ditangani",
                                 "on_time": "% tepat waktu", "level": ""})
        polish(fig, legend=dict(orientation="h", y=1.14))
        chart(fig)
        st.caption("Sumbu X = pengalaman (jumlah proyek), Y = kualitas delivery "
                   "(% tepat waktu). Kiri-bawah = konsultan yang perlu pendampingan.")

    with c2:
        sec("🧭", "Komposisi tim per role & level", C_TEAL)
        komp = konsultan.groupby(["role", "level"]).size().reset_index(name="n")
        fig = px.bar(komp, x="role", y="n", color="level", barmode="stack",
                     color_discrete_map={"Senior": "#1E40AF", "Mid": "#0F766E",
                                         "Junior": "#94A3B8"},
                     labels={"n": "Orang", "role": "", "level": ""})
        polish(fig, legend=dict(orientation="h", y=1.15))
        chart(fig)

        sec("📋", "Leaderboard delivery", C_PURPLE)
        lb = (perf.sort_values(["on_time", "proyek"], ascending=False)
              [["id_konsultan", "role", "level", "proyek", "on_time", "dev_pct"]]
              .head(10))
        lb.columns = ["Konsultan", "Role", "Level", "Proyek",
                      "% Tepat", "Deviasi %"]
        lb["% Tepat"] = lb["% Tepat"].round(0)
        lb["Deviasi %"] = lb["Deviasi %"].round(1)
        table(lb)

    penjelasan("Cara membaca bagian ini", """
**Bubble chart konsultan** memetakan dua dimensi sekaligus: beban kerja
(jumlah proyek) dan kualitas delivery (% tepat waktu). Kuadran ideal:
kanan-atas (banyak proyek, tetap tepat waktu) = konsultan andalan untuk
proyek besar.

**Deviasi budget per konsultan** melengkapi gambar: konsultan yang tepat
waktu TAPI sering overrun punya masalah estimasi scope; yang tepat waktu
DAN on-budget adalah delivery paling sehat.
""")

    _lv = (perf.groupby("level")
           .apply(lambda g: pd.Series({"ot": 100 * (g["on_time"] * g["proyek"]).sum()
                                       / g["proyek"].sum(),
                                       "n": g["proyek"].sum()}),
                  include_groups=False))
    if len(_lv) >= 2:
        insight_box("Ketepatan go-live per level PIC: " + " · ".join(
            f"<b>{lv}</b> {r['ot']:.0f}% ({int(r['n'])} proyek)"
            for lv, r in _lv.sort_values("ot", ascending=False).iterrows())
            + ". Model bisnis konsultan adalah <i>people business</i> — "
              "pairing junior-senior dan dokumentasi menekan risiko "
              "knowledge silo.", "blue")

# ------------------------------------------------------------------ #
#  TAB 5 — Prediktif & Eksplorasi                                     #
# ------------------------------------------------------------------ #
@st.cache_data
def train_delay_model():
    d = proyek.dropna(subset=["tanggal_golive"]).merge(
        konsultan[["id_konsultan", "level"]], on="id_konsultan")
    d["late"] = (d["status_proyek"] == "Go-live Terlambat").astype(int)
    feats = pd.get_dummies(
        d[["produk", "modul_utama", "durasi_target_hari", "level"]],
        drop_first=True).astype(float)
    y = d["late"]
    rf = RandomForestClassifier(n_estimators=300, max_depth=3,
                                min_samples_leaf=10, random_state=7, n_jobs=-1)
    cv = StratifiedKFold(5, shuffle=True, random_state=7)
    aucs = cross_val_score(rf, feats, y, cv=cv, scoring="roc_auc")
    prob = cross_val_predict(rf, feats, y, cv=cv, method="predict_proba")[:, 1]
    rf.fit(feats, y)
    imp = (pd.Series(rf.feature_importances_, index=feats.columns)
           .nlargest(10).sort_values().reset_index())
    imp.columns = ["fitur", "penting"]
    return (aucs.mean(), aucs.std()), imp, y.to_numpy(), prob

with tab5:
    c1, c2 = st.columns(2, gap="large")

    with c1:
        sec("📈", "Proyeksi lead 2026–2028", C_PURPLE)
        tr = ld.groupby("tahun").size().reset_index(name="n")
        if len(tr) >= 3:
            X = sm.add_constant(tr["tahun"].astype(float))
            ols = sm.OLS(tr["n"].astype(float), X).fit()
            fut = pd.DataFrame({"tahun": [2026., 2027., 2028.]})
            pr = ols.get_prediction(sm.add_constant(fut)).summary_frame(alpha=0.1)
            fut["pred"] = pr["mean"].round(0).astype(int)
            fut["lo"], fut["hi"] = pr["obs_ci_lower"], pr["obs_ci_upper"]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=tr["tahun"], y=tr["n"],
                                     mode="lines+markers", name="Aktual",
                                     line=dict(color=C_BLUE, width=3.5),
                                     marker=dict(size=9)))
            fig.add_trace(go.Scatter(
                x=pd.concat([fut["tahun"], fut["tahun"][::-1]]),
                y=pd.concat([fut["hi"], fut["lo"][::-1]]),
                fill="toself", fillcolor="rgba(15,118,110,.12)",
                line=dict(width=0), name="Interval 90%", hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=fut["tahun"], y=fut["pred"],
                                     mode="lines+markers", name="Proyeksi",
                                     line=dict(color=C_PURPLE, width=3,
                                               dash="dash"),
                                     marker=dict(size=9, symbol="diamond")))
            polish(fig, legend=dict(orientation="h", y=1.14),
                   yaxis_title="Leads")
            chart(fig)
            st.caption("OLS pada tren lead historis — baseline perencanaan "
                       "kapasitas sales & delivery.")
        else:
            st.info("Butuh minimal 3 tahun data untuk proyeksi.")

        sec("🤖", "Prediktor keterlambatan proyek (Random Forest)", C_RED)
        auc, imp, y_true, y_prob = train_delay_model()
        fig = px.bar(imp, x="penting", y="fitur", orientation="h",
                     color="penting", color_continuous_scale="Teal",
                     text=imp["penting"].map("{:.2f}".format),
                     labels={"fitur": "", "penting": "Feature importance"})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        chart(fig)
        st.caption(f"ROC-AUC (5-fold CV): **{auc[0]:.2f} ± {auc[1]:.2f}** — "
                   "sinyal ada tetapi **moderat**: cocok untuk triase risiko "
                   "sejak kickoff (fitur: produk, modul, durasi target, level "
                   "PIC), bukan untuk keputusan tunggal. Probabilitas dihitung "
                   "out-of-fold sehingga tidak bocor.")

        sec("🎚️", "Threshold & trade-off deteksi delay", C_AMBER)
        thr = st.slider("Threshold klasifikasi delay", 0.10, 0.90, 0.50, 0.05,
                        help="Di atas threshold → diprediksi terlambat. Turunkan "
                             "untuk menangkap lebih banyak proyek berisiko.")
        y_hat = (y_prob >= thr).astype(int)
        tp = int(((y_hat == 1) & (y_true == 1)).sum())
        fp = int(((y_hat == 1) & (y_true == 0)).sum())
        fn = int(((y_hat == 0) & (y_true == 1)).sum())
        tn = int(((y_hat == 0) & (y_true == 0)).sum())
        prec = tp / max(tp + fp, 1)
        rec = tp / max(tp + fn, 1)
        f1 = 2 * prec * rec / max(prec + rec, 1e-9)
        m1, m2, m3 = st.columns(3)
        m1.metric("Recall (telat terdeteksi)", f"{100*rec:.0f}%")
        m2.metric("Precision (flag tepat)", f"{100*prec:.0f}%")
        m3.metric("F1-score", f"{f1:.2f}")
        cm = pd.DataFrame([[tn, fp], [fn, tp]],
                          index=["Aktual: tepat", "Aktual: telat"],
                          columns=["Pred: tepat", "Pred: telat"])
        fig = px.imshow(cm, text_auto=True, aspect="auto",
                        color_continuous_scale="Blues",
                        labels=dict(color="n"))
        fig.update_layout(height=270)
        polish(fig, coloraxis_showscale=False)
        chart(fig)

    with c2:
        sec("🔍", "Eksplorasi data interaktif", C_PURPLE)
        st.caption("Bangun tabel analisis sendiri.")
        tabel_map = {"leads": ld, "opportunities": op, "proyek": pj,
                     "tiket": tk}
        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            tabel_pilih = st.selectbox("Tabel", list(tabel_map))
        base = tabel_map[tabel_pilih]
        with ec2:
            dims = st.multiselect("Dimensi (group by)",
                                  base.columns.tolist(),
                                  default=[base.columns[4]])
        with ec3:
            opsi_metrik = ["Jumlah baris"] + [
                c for c in base.columns
                if base[c].dtype.kind == "bif"]
            metrik = st.selectbox("Metrik (rata-rata)",
                                  ["Jumlah baris"] + [f"Rata-rata {c}"
                                                     for c in opsi_metrik[1:]])
        if dims:
            g = base.groupby(dims)
            res = (g.size().reset_index(name="jumlah")
                   if metrik == "Jumlah baris"
                   else g[metrik.replace("Rata-rata ", "")].mean()
                   .round(2).reset_index(name="rata_rata"))
            table(res)
            st.download_button("⬇️ Download (CSV)", res.to_csv(index=False),
                               "hasil_eksplorasi.csv", "text/csv")

        st.divider()
        sec("🗃️", "Pratinjau data", C_TEAL)
        pilihan = st.selectbox("Tabel preview", list(tabel_map),
                               key="pv", label_visibility="collapsed")
        table(tabel_map[pilihan].head(100), height=300)

    penjelasan("Cara membaca bagian ini", """
**Delay predictor** menjawab pertanyaan delivery paling penting: *proyek
mana yang berisiko telat SEJAK kickoff?* Fitur model hanya yang diketahui
saat proyek dimulai (produk, industri, modul, durasi target, budget,
level konsultan PIC) — bisa dipakai untuk alokasi PM senior ke proyek
berisiko.

**Forecast** baseline untuk perencanaan: berapa konsultan & sales yang
dibutuhkan 1-2 tahun ke depan jika tren lead berlanjut.

⚠️ Model dilatih di data sintetis — mekanismenya nyata, angkanya simulasi.
""")

    insight_box("Pola pikir delivery senior: <b>prediksi delay saat kickoff</b>, "
                "bukan reaktif saat proyek sudah telat — mitigasi jauh lebih murah "
                "di awal proyek.", "green")

# ------------------------------------------------------------------ #
#  Footer                                                             #
# ------------------------------------------------------------------ #
st.markdown(
    '<div class="footer"><span><b>ERP Consulting Performance</b> — '
    'portfolio project · konteks PT Beone Optima Solusi, data sintetis</span>'
    '<span>Streamlit · Plotly · SQLite · scikit-learn</span></div>',
    unsafe_allow_html=True)
