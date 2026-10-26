"""
Generator dataset sintetis: ERP Consulting Performance — PT Beone Optima Solusi.

DISCLAIMER: 100% data sintetis. Struktur & distribusi dimodelkan dari informasi
publik (beonesolution.com, profil partner SAP, portal rekrutmen). TIDAK
merepresentasikan data, klien, pendapatan, atau kinerja aktual perusahaan.

Model bisnis: funnel B2B konsultan ERP
    lead -> opportunity -> (won) -> proyek implementasi -> go-live -> tiket support

Tabel:
    leads         ~2.800 baris  (2019-2025, sumber akuisisi, industri, status)
    opportunities ~1.200 baris  (pipeline: stage, nilai deal, sales cycle)
    proyek        ~520 baris    (implementasi: jadwal vs aktual, budget vs aktual)
    tiket         ~4.800 baris  (support: kategori, prioritas, SLA, resolusi)
    konsultan     ~36 baris     (dimensi tim: role, level)
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
TAHUN = list(range(2019, 2026))

# ------------------------------------------------------------------ #
#  Referensi konteks (dari riset publik)                              #
# ------------------------------------------------------------------ #
# Industri yang dilayani (profil SAP + situs): manufaktur, distribusi,
# retail, pertambangan, konstruksi, jasa profesional, F&B, agrikultur
INDUSTRI = {
    "Manufaktur":        0.30,
    "Trading/Distribusi": 0.20,
    "Retail":            0.13,
    "F&B":               0.10,
    "Konstruksi":        0.09,
    "Pertambangan":      0.06,
    "Agrikultur":        0.06,
    "Jasa Profesional":  0.06,
}
# Produk: SAP B1 dominan; S/4HANA GROW ~2023; Business Insight = produk
# in-house (App Store ~2024); TSplus = distributor resmi; add-on kecil
PRODUK = ["SAP Business One", "SAP S/4HANA GROW", "Add-on & Integrasi",
          "Business Insight", "TSplus", "Training/Xpertise Academy"]
# Sumber lead: bukti publik = telemarketing intern, workshop Business Hacks,
# website; referral khas bisnis konsultan
SUMBER = ["Website", "Referral Klien", "Event/Workshop", "Telemarketing",
          "LinkedIn", "Partner SAP"]
# Kota klien (kantor Tangerang -> Jabodetabek dominan + industri Jabar/Jatim)
KOTA = {
    "Jakarta": 0.20, "Tangerang": 0.15, "Bekasi": 0.10, "Bogor": 0.07,
    "Karawang": 0.07, "Depok": 0.06, "Bandung": 0.08, "Cikarang": 0.06,
    "Surabaya": 0.07, "Semarang": 0.04, "Cikupa": 0.04,
    "Sidoarjo": 0.03, "Batam": 0.03,
}

# Volume lead per tahun: tumbuh (award Fastest Growing 2018-2020)
N_LEAD = {2019: 260, 2020: 300, 2021: 350, 2022: 420,
          2023: 480, 2024: 520, 2025: 570}

# Probabilitas produk per tahun
def prob_produk(tahun):
    if tahun <= 2022:
        return [0.72, 0.06, 0.11, 0.00, 0.07, 0.04]
    if tahun <= 2024:
        return [0.60, 0.15, 0.11, 0.04, 0.06, 0.04]   # BI mulai ~2023
    return [0.52, 0.21, 0.10, 0.06, 0.05, 0.06]

# Tren sumber akuisisi (digital naik, telemarketing melandai)
def prob_sumber(tahun):
    base = {"Website": 0.22, "Referral Klien": 0.18, "Event/Workshop": 0.16,
            "Telemarketing": 0.20, "LinkedIn": 0.10, "Partner SAP": 0.14}
    if tahun >= 2022:
        base["Event/Workshop"] += 0.06   # Business Hacks 2022 dst.
        base["Telemarketing"] -= 0.04
        base["LinkedIn"] += 0.03
        base["Website"] -= 0.05
    w = np.array([base[s] for s in SUMBER]); return w / w.sum()

# Win rate per sumber (referral & event = lead hangat; telemarketing dingin)
WIN_RATE_SUMBER = {"Referral Klien": 0.34, "Event/Workshop": 0.30,
                   "Partner SAP": 0.28, "Website": 0.22,
                   "LinkedIn": 0.18, "Telemarketing": 0.12}

# Nilai deal per produk (juta IDR, lognormal-ish) — parameter skenario
DEAL = {"SAP Business One":    dict(mu=5.7, sigma=0.55),   # median ~300jt
        "SAP S/4HANA GROW":    dict(mu=6.8, sigma=0.50),   # median ~900jt
        "Add-on & Integrasi":  dict(mu=4.7, sigma=0.60),   # median ~110jt
        "Business Insight":    dict(mu=4.3, sigma=0.50),   # median ~75jt
        "TSplus":              dict(mu=3.5, sigma=0.55),   # median ~33jt
        "Training/Xpertise Academy": dict(mu=3.9, sigma=0.45)}  # ~50jt

def sample_deal(produk, n=1):
    p = DEAL[produk]
    return np.exp(rng.normal(p["mu"], p["sigma"], n)).round(0)

# ------------------------------------------------------------------ #
#  1. Konsultan (dimensi tim)                                         #
# ------------------------------------------------------------------ #
ROLE = (["Functional Consultant"] * 14 + ["Technical Consultant"] * 8 +
        ["Project Manager"] * 5 + ["Support Engineer"] * 9)
LEVEL = (["Junior"] * 12 + ["Mid"] * 16 + ["Senior"] * 8)
konsultan = pd.DataFrame({
    "id_konsultan": [f"K{ i+1:03d}" for i in range(36)],
    "role": ROLE, "level": LEVEL,
    "tahun_gabung": rng.choice(range(2015, 2025), 36,
                               p=np.linspace(1, 14, 10) / np.linspace(1, 14, 10).sum()),
})
konsultan.to_csv("data/raw/konsultan.csv", index=False)

# ------------------------------------------------------------------ #
#  2. Leads                                                           #
# ------------------------------------------------------------------ #
rows, lid = [], 0
for th in TAHUN:
    n = N_LEAD[th]
    for _ in range(n):
        lid += 1
        sumber = rng.choice(SUMBER, p=prob_sumber(th))
        industri = rng.choice(list(INDUSTRI), p=list(INDUSTRI.values()))
        produk = rng.choice(PRODUK, p=prob_produk(th))
        kota = rng.choice(list(KOTA), p=list(KOTA.values()))
        bulan = int(rng.integers(1, 13))
        win = rng.random() < WIN_RATE_SUMBER[sumber]
        # lead yang kalah bisa berhenti di stage lebih awal
        if not win:
            status_lead = rng.choice(["Lost - no budget", "Lost - kompetitor",
                                      "Cold/tidak responsif"], p=[0.35, 0.3, 0.35])
        else:
            status_lead = "Converted"
        rows.append([f"L{lid:05d}", th, bulan, sumber, industri, kota,
                     produk, status_lead])
leads = pd.DataFrame(rows, columns=[
    "id_lead", "tahun", "bulan", "sumber", "industri", "kota",
    "produk_minat", "status_lead"])

# ------------------------------------------------------------------ #
#  3. Opportunities (hanya dari lead yg lolos kualifikasi awal)       #
# ------------------------------------------------------------------ #
# ~55% lead masuk pipeline resmi; lead Lost bisa tetap punya opp yang kalah
opp_rows, oid = [], 0
for _, r in leads.iterrows():
    masuk_pipeline = rng.random() < (0.62 if r.status_lead == "Converted" else 0.35)
    if not masuk_pipeline:
        continue
    oid += 1
    won = r.status_lead == "Converted"
    # sales cycle: S4HANA lebih panjang; produk ringan lebih singkat
    mu_cycle = {"SAP Business One": 105, "SAP S/4HANA GROW": 170,
                "Add-on & Integrasi": 60, "Business Insight": 45,
                "TSplus": 20, "Training/Xpertise Academy": 25}[r.produk_minat]
    cycle = max(10, int(rng.normal(mu_cycle, mu_cycle * 0.30)))
    nilai = float(sample_deal(r.produk_minat)[0])
    tgl_buat = pd.Timestamp(int(r.tahun), int(r.bulan),
                            int(rng.integers(1, 28)))
    tgl_close = tgl_buat + pd.Timedelta(days=cycle)
    # Entitas: PT CORE (sister company, berdiri ~Okt 2023) mengambil alih
    # sebagian implementasi SAP B1 sejak 2024 — pola spin-off riil
    entitas = "BeOne HQ"
    if r.tahun >= 2024 and r.produk_minat == "SAP Business One":
        entitas = rng.choice(["BeOne HQ", "PT CORE (sister)"], p=[0.7, 0.3])
    opp_rows.append([f"O{oid:05d}", r.id_lead, r.produk_minat, entitas,
                     nilai, "Won" if won else "Lost",
                     tgl_buat.date(), tgl_close.date(), cycle])
opportunities = pd.DataFrame(opp_rows, columns=[
    "id_opportunity", "id_lead", "produk", "entitas", "nilai_deal_jt",
    "hasil", "tanggal_buat", "tanggal_close", "sales_cycle_hari"])

# ------------------------------------------------------------------ #
#  4. Proyek implementasi (dari opp Won)                              #
# ------------------------------------------------------------------ #
MODUL = {
    "SAP Business One": ["Financials", "Sales", "Purchasing", "Inventory",
                          "Production", "Reporting"],
    "SAP S/4HANA GROW": ["Finance", "Manufacturing/MRP", "Procurement",
                          "Sales & Distribution", "Analytics"],
    "Add-on & Integrasi": ["Coretax", "Plant Maintenance", "POS Integration",
                            "WMS", "E-Commerce Link"],
    "Business Insight": ["Dashboard & Reporting", "Mobile Analytics",
                          "KPI Monitoring"],
    "TSplus": ["Remote Access", "Advanced Security", "Server Farm"],
    "Training/Xpertise Academy": ["SAP B1 End-User", "SAP B1 Functional",
                                   "Campus Seminar/Workshop", "In-house Training"],
}
PRODUK_RISK = {"SAP Business One": 0.03, "SAP S/4HANA GROW": 0.14,
               "Add-on & Integrasi": 0.10, "Business Insight": -0.02,
               "TSplus": -0.10, "Training/Xpertise Academy": -0.08}
MODUL_RISIKO_TINGGI = {"Production", "Manufacturing/MRP", "Procurement",
                       "Purchasing", "Coretax", "POS Integration", "WMS",
                       "E-Commerce Link"}
LEVEL_RISK = {"Senior": -0.10, "Mid": 0.0, "Junior": 0.12}
proyek_rows, pid = [], 0
for _, o in opportunities[opportunities.hasil == "Won"].iterrows():
    if rng.random() > 0.88:      # sebagian deal batal sebelum kickoff
        continue
    pid += 1
    ld = leads.set_index("id_lead").loc[o.id_lead]
    modul = rng.choice(MODUL[o.produk])
    # durasi implementasi: B1 3-8 bln, S4HANA 6-14 bln, add-on 1-3 bln
    mu_dur = {"SAP Business One": 160, "SAP S/4HANA GROW": 300,
              "Add-on & Integrasi": 60, "Business Insight": 45,
              "TSplus": 15, "Training/Xpertise Academy": 20}[o.produk]
    dur_target = max(20, int(rng.normal(mu_dur, mu_dur * 0.18)))
    kons = konsultan[konsultan.role.isin(
        ["Project Manager", "Functional Consultant"])].sample(
        1, random_state=int(rng.integers(1_000_000_000)))
    # Probabilitas telat = base + penyesuaian faktor risiko (ASUMSI MODEL,
    # terdokumentasi di docs/DATA_DICTIONARY.md): kompleksitas produk &
    # modul, level PIC, dan durasi target yang panjang.
    p_late = (0.28 + PRODUK_RISK[o.produk]
              + (0.08 if modul in MODUL_RISIKO_TINGGI else 0.0)
              + LEVEL_RISK[kons.iloc[0].level]
              + (0.08 if dur_target > mu_dur * 1.15 else 0.0))
    p_late = float(np.clip(p_late, 0.05, 0.85))
    if rng.random() < p_late:
        delay = rng.uniform(0.05, 0.45) * dur_target   # telat 5-45%
    else:
        delay = -rng.uniform(0.0, 0.12) * dur_target   # tepat/lebih cepat
    dur_aktual = int(dur_target + delay)
    tgl_mulai = pd.Timestamp(o.tanggal_close) + pd.Timedelta(
        days=int(rng.integers(5, 45)))
    tgl_target = tgl_mulai + pd.Timedelta(days=dur_target)
    tgl_golive = tgl_mulai + pd.Timedelta(days=dur_aktual)
    budget = float(o.nilai_deal_jt)
    overrun = rng.random() < 0.28
    aktual = round(budget * (rng.uniform(1.03, 1.30) if overrun
                             else rng.uniform(0.92, 1.02)), 0)
    selesai = tgl_golive <= pd.Timestamp("2026-01-01")
    status = ("On Progress" if not selesai else
              ("Go-live Tepat Waktu" if dur_aktual <= dur_target
               else "Go-live Terlambat"))
    proyek_rows.append([f"P{pid:05d}", o.id_opportunity, ld.industri,
                        o.produk, o.entitas, modul, kons.iloc[0].id_konsultan,
                        tgl_mulai.date(), tgl_target.date(),
                        tgl_golive.date() if selesai else None,
                        dur_target, dur_aktual if selesai else None,
                        budget, aktual if selesai else budget,
                        status])
proyek = pd.DataFrame(proyek_rows, columns=[
    "id_proyek", "id_opportunity", "industri", "produk", "entitas",
    "modul_utama",
    "id_konsultan", "tanggal_mulai", "target_golive", "tanggal_golive",
    "durasi_target_hari", "durasi_aktual_hari", "budget_jt", "aktual_jt",
    "status_proyek"])

# ------------------------------------------------------------------ #
#  5. Tiket support (hypercare spike pasca go-live)                   #
# ------------------------------------------------------------------ #
KATEGORI = {"How-to/Training": 0.30, "Error/Bug": 0.24, "Laporan/Query": 0.16,
            "Integrasi/Add-on": 0.16, "Akses/Authorisasi": 0.14}
PRIORITAS = {"Critical": 0.08, "High": 0.27, "Medium": 0.40, "Low": 0.25}
SLA_JAM = {"Critical": 8, "High": 24, "Medium": 48, "Low": 96}
tiket_rows, tid = [], 0
golive_done = proyek.dropna(subset=["tanggal_golive"])
for _, p in golive_done.iterrows():
    # Hypercare lebih berat pada proyek yang go-live-nya terlambat
    # (ASUMSI MODEL: rata-rata 12,5 vs 8,5 tiket)
    lam = 12.5 if p.status_proyek == "Go-live Terlambat" else 8.5
    n_tiket = max(3, int(rng.poisson(lam)))
    t0 = pd.Timestamp(p.tanggal_golive)
    for _ in range(n_tiket):
        tid += 1
        # 60% tiket muncul dalam 90 hari pertama (hypercare)
        hari = int(rng.exponential(55)) if rng.random() < 0.6 else \
            int(rng.integers(90, 365))
        kat = rng.choice(list(KATEGORI), p=list(KATEGORI.values()))
        pri = rng.choice(list(PRIORITAS), p=list(PRIORITAS.values()))
        sla = SLA_JAM[pri]
        # resolusi: junior lebih lambat; critical diprioritaskan
        mu_res = sla * 0.55
        jam_res = round(max(1, float(rng.gamma(2.2, mu_res / 2.2))), 1)
        tiket_rows.append([f"T{tid:05d}", p.id_proyek, p.industri, p.produk,
                           kat, pri,
                           (t0 + pd.Timedelta(days=hari)).date(),
                           jam_res, sla, jam_res <= sla])
tiket = pd.DataFrame(tiket_rows, columns=[
    "id_tiket", "id_proyek", "industri", "produk", "kategori",
    "prioritas", "tanggal_dibuat", "jam_resolusi", "sla_jam",
    "sla_tercapai"])

leads.to_csv("data/raw/leads.csv", index=False)
opportunities.to_csv("data/raw/opportunities.csv", index=False)
proyek.to_csv("data/raw/proyek.csv", index=False)
tiket.to_csv("data/raw/tiket.csv", index=False)

print("leads        :", len(leads))
print("opportunities:", len(opportunities))
print("proyek       :", len(proyek))
print("tiket        :", len(tiket))
print("konsultan    :", len(konsultan))
print("win rate     :",
      round(100 * (opportunities.hasil == "Won").mean(), 1), "%")
print("on-time go-live:",
      round(100 * (golive_done.status_proyek == "Go-live Tepat Waktu").mean(), 1), "%")
print("SLA tercapai :", round(100 * tiket.sla_tercapai.mean(), 1), "%")
