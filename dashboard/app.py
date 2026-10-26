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
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="BeOne ERP Analytics", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")

C_BLUE, C_CYAN, C_TEAL = "#3B82F6", "#06B6D4", "#14B8A6"
C_GREEN, C_AMBER, C_ORANGE = "#22C55E", "#F59E0B", "#F97316"
C_PINK, C_PURPLE, C_RED = "#EC4899", "#8B5CF6", "#EF4444"
PALETTE = [C_BLUE, C_CYAN, C_GREEN, C_AMBER, C_PINK, C_PURPLE, C_ORANGE, C_TEAL]
PRODUK_COLOR = {"SAP Business One": C_BLUE, "SAP S/4HANA GROW": C_PURPLE,
                "Add-on & Integrasi": C_AMBER, "Business Insight": C_GREEN,
                "TSplus": C_CYAN}

st.markdown("""
<style>
    .block-container {padding-top:0;padding-bottom:2rem;max-width:1280px;}
    [data-testid="stSidebar"] {
        background:linear-gradient(180deg,#0C4A6E 0%,#155E75 55%,#134E4A 100%);}
    [data-testid="stSidebar"] * {color:#EFFBFF !important;}
    [data-testid="stSidebar"] .stMultiSelect label {font-weight:600;}
    .hero {
        background:linear-gradient(115deg,#0369A1 0%,#0D9488 45%,#22C55E 110%);
        border-radius:20px;padding:2.3rem 2.4rem 1.9rem;margin:1rem 0 1.5rem;
        color:white;box-shadow:0 14px 34px rgba(13,148,136,.30);
        position:relative;overflow:hidden;}
    .hero::after {content:"";position:absolute;right:-70px;top:-70px;
        width:230px;height:230px;border-radius:50%;background:rgba(255,255,255,.14);}
    .hero::before {content:"";position:absolute;right:60px;bottom:-90px;
        width:170px;height:170px;border-radius:50%;background:rgba(255,255,255,.10);}
    .hero h1 {margin:0;font-size:2rem;font-weight:900;letter-spacing:.3px;}
    .hero p  {margin:.55rem 0 0;font-size:1rem;opacity:.93;}
    .kpi {border-radius:16px;padding:1.1rem 1.2rem 1rem;height:100%;color:white;
        box-shadow:0 6px 18px rgba(22,32,46,.12);position:relative;overflow:hidden;}
    .kpi::after {content:"";position:absolute;right:-30px;top:-30px;
        width:90px;height:90px;border-radius:50%;background:rgba(255,255,255,.18);}
    .kpi .label {font-size:.76rem;font-weight:700;opacity:.92;
        text-transform:uppercase;letter-spacing:.7px;}
    .kpi .value {font-size:1.8rem;font-weight:900;line-height:1.15;}
    .kpi .sub   {font-size:.8rem;opacity:.88;margin-top:.15rem;}
    .sec-pill {display:inline-block;font-size:1.05rem;font-weight:800;
        color:#16202E;margin:.5rem 0 .3rem;padding:.15rem .8rem .15rem 0;}
    .sec-pill::before {content:"●";margin-right:.45rem;font-size:.9rem;}
    .insight {border-radius:0 12px 12px 0;padding:.8rem 1rem;font-size:.88rem;
        margin:.6rem 0;}
    .insight.blue  {background:#EAF2FF;border-left:4px solid #3B82F6;color:#274C8E;}
    .insight.green {background:#E9F9F0;border-left:4px solid #22C55E;color:#166534;}
    .insight.amber {background:#FFF6E5;border-left:4px solid #F59E0B;color:#92580A;}
    .insight b {font-weight:800;}
    .stTabs [data-baseweb="tab-list"] {gap:.45rem;}
    .stTabs [data-baseweb="tab"] {background:#ECECF6;border-radius:10px 10px 0 0;
        padding:.45rem 1.1rem;font-weight:700;color:#5A5F7E;}
    .stTabs [aria-selected="true"] {
        background:linear-gradient(120deg,#0D9488,#0369A1) !important;
        color:white !important;}
    [data-testid="stExpander"] {background:#FFF;border-radius:12px;
        border:1px solid #E6E8F2;}
    [data-testid="stDataFrame"] {border-radius:12px;overflow:hidden;
        border:1px solid #E6E8F2;}
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
    font=dict(family="Inter, Segoe UI, sans-serif", size=13, color="#16202E"),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=46, b=10),
    title=dict(font=dict(size=15, color="#16202E")),
    colorway=PALETTE)

def polish(fig, **kw):
    fig.update_layout(**{**BASE_LAYOUT, **kw})
    fig.update_xaxes(showgrid=False, zeroline=False, automargin=True)
    fig.update_yaxes(gridcolor="#ECECF6", zeroline=False, automargin=True,
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

def sec(icon, label, color):
    st.markdown(f'<div class="sec-pill" style="color:{color}">{icon} '
                f'<span style="color:#16202E">{label}</span></div>',
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
  <h1>📊 ERP Consulting Performance</h1>
  <p>Analisis funnel & delivery konsultan ERP — konteks PT Beone Optima Solusi
     (SAP Gold Partner) · 2019–2025 · data sintetis</p>
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

GRAD = {
    "blue":   "linear-gradient(135deg,#3B82F6 0%,#2563EB 100%)",
    "teal":   "linear-gradient(135deg,#14B8A6 0%,#0D9488 100%)",
    "amber":  "linear-gradient(135deg,#F59E0B 0%,#F97316 100%)",
    "purple": "linear-gradient(135deg,#8B5CF6 0%,#7C3AED 100%)",
    "pink":   "linear-gradient(135deg,#EC4899 0%,#EF4444 120%)",
}
kpis = [
    ("🧲 Total Leads", titik(n_lead), f"{len(th_pilih)} tahun", GRAD["blue"]),
    ("💼 Pipeline Value", miliar(pipeline_jt), f"{titik(n_opp)} opportunity", GRAD["teal"]),
    ("🏆 Win Rate", f"{100*n_won/max(n_opp,1):.1f}%".replace(".", ","),
     f"{miliar(won_jt)} revenue won", GRAD["amber"]),
    ("🚀 On-time Go-live", f"{on_time:.0f}%", f"{len(pj_done)} proyek selesai", GRAD["purple"]),
    ("⏱️ SLA Support", f"{sla_pct:.0f}%", f"{titik(len(tk))} tiket", GRAD["pink"]),
]
for col, (label, val, sub, grad) in zip(st.columns(5), kpis):
    col.markdown(f"""
    <div class="kpi" style="background:{grad}">
        <div class="label">{label}</div>
        <div class="value">{val}</div>
        <div class="sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

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
            marker=dict(color=[C_BLUE, C_CYAN, C_GREEN, C_AMBER]),
            connector=dict(line=dict(color="#D6D8F0", width=2))))
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

    sec("�", "Revenue won per entitas (struktur grup)", C_PINK)
    ent = (op[op.hasil == "Won"]
           .join(ld.set_index("id_lead")["tahun"], on="id_lead")
           .groupby(["tahun", "entitas"])["nilai_deal_jt"].sum()
           .reset_index())
    fig = px.bar(ent, x="tahun", y="nilai_deal_jt", color="entitas",
                 barmode="stack",
                 color_discrete_map={"BeOne HQ": C_BLUE,
                                     "PT CORE (sister)": C_PINK},
                 labels={"nilai_deal_jt": "Revenue (Rp jt)", "tahun": "",
                         "entitas": ""})
    polish(fig, legend=dict(orientation="h", y=1.14))
    chart(fig)
    st.caption("PT CORE = sister company yang berdiri ~2023 dan mengambil "
               "alih sebagian implementasi SAP B1 sejak 2024.")

    sec("�🏭", "Pipeline per industri × produk", C_ORANGE)
    heat = (op.join(ld.set_index("id_lead")["industri"], on="id_lead")
            .groupby(["industri", "produk"])["nilai_deal_jt"].sum()
            .unstack(fill_value=0))
    fig = px.imshow(heat, aspect="auto", color_continuous_scale="Turbo",
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
                    f"(win rate {_wr['wr']:.0f}%). Referral & event selalu "
                    "mengalahkan cold outreach di B2B consulting.", "blue")

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
                     color="late", color_continuous_scale="Sunset",
                     text=md["late"].map("{:.0f}%".format),
                     labels={"late": "% terlambat", "modul_utama": ""})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        chart(fig)

    penjelasan("Cara membaca bagian ini", """
**On-time go-live** adalah KPI paling kritis di bisnis implementasi ERP —
telat = biaya konsultan membengkak + kepercayaan klien turun. Benchmark
industri: 40-60% proyek ERP terlambat; perusahaan dengan delivery matang
menjaga angka ini di bawah 40%.

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

    insight_box("Keterlambatan proyek ERP jarang soal coding — biasanya "
                "<b>scope creep, kesiapan data master klien, dan sign-off UAT</b>. "
                "Modul integrasi paling rentan karena bergantung pada sistem "
                "pihak ketiga.", "amber")

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
                     color_discrete_map={"Critical": C_RED, "High": C_ORANGE,
                                         "Medium": C_AMBER, "Low": C_GREEN},
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
                     color_discrete_map={"Critical": C_RED, "High": C_ORANGE,
                                         "Medium": C_AMBER, "Low": C_GREEN},
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
                     color="tpp", color_continuous_scale="Emrld",
                     text=tb["tpp"].map("{:.1f}".format),
                     labels={"tpp": "Tiket per proyek", "industri": ""})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        chart(fig)

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
                         color_discrete_map={"Senior": C_GREEN, "Mid": C_BLUE,
                                             "Junior": C_AMBER},
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
                     color_discrete_map={"Senior": C_GREEN, "Mid": C_BLUE,
                                         "Junior": C_AMBER},
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

    insight_box("Model bisnis konsultan = <b>people business</b>: delivery "
                "berkualitas terkonsentrasi di segelintir konsultan senior. "
                "Risiko kunci: knowledge silo — dokumentasi & pairing "
                "junior-senior adalah mitigasinya.", "blue")

# ------------------------------------------------------------------ #
#  TAB 5 — Prediktif & Eksplorasi                                     #
# ------------------------------------------------------------------ #
@st.cache_data
def train_delay_model():
    d = proyek.dropna(subset=["tanggal_golive"]).merge(
        konsultan[["id_konsultan", "level"]], on="id_konsultan")
    d["late"] = (d["status_proyek"] == "Go-live Terlambat").astype(int)
    feats = pd.get_dummies(
        d[["produk", "industri", "modul_utama", "durasi_target_hari",
           "budget_jt", "level"]], drop_first=True)
    y = d["late"]
    Xtr, Xte, ytr, yte = train_test_split(
        feats, y, test_size=0.3, random_state=7, stratify=y)
    rf = RandomForestClassifier(n_estimators=200, max_depth=6,
                                random_state=7, n_jobs=-1).fit(Xtr, ytr)
    auc = roc_auc_score(yte, rf.predict_proba(Xte)[:, 1])
    imp = (pd.Series(rf.feature_importances_, index=feats.columns)
           .nlargest(10).sort_values().reset_index())
    imp.columns = ["fitur", "penting"]
    return auc, imp

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
                fill="toself", fillcolor="rgba(139,92,246,.15)",
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
        auc, imp = train_delay_model()
        fig = px.bar(imp, x="penting", y="fitur", orientation="h",
                     color="penting", color_continuous_scale="Sunset",
                     text=imp["penting"].map("{:.2f}".format),
                     labels={"fitur": "", "penting": "Feature importance"})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        chart(fig)
        st.caption(f"ROC-AUC test set: **{auc:.2f}** — model flag risiko delay "
                   "sejak kickoff (fitur: produk, industri, modul, durasi target, "
                   "budget, level PIC).")

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
