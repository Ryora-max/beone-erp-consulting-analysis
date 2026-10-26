# ERP Consulting Performance Analytics — PT Beone Optima Solusi

Portofolio Data Analyst: analisis end-to-end bisnis konsultan ERP B2B —
dari **lead generation → sales pipeline → delivery implementasi →
go-live → managed support**, dengan konteks perusahaan nyata
**PT Beone Optima Solusi (BeOne Solution)**, SAP Gold Partner di Tangerang.

> ⚠️ **Disclaimer:** dataset **100% sintetis** (seed=42). Struktur bisnis
> dikalibrasi dari informasi publik — lihat `docs/SUMBER_DATA.md`.
> Proyek ini **tidak berafiliasi** dengan perusahaan dan tidak
> merepresentasikan data/kinerja riilnya.

## Pertanyaan bisnis yang dijawab

1. Sumber lead mana yang paling efektif menghasilkan deal (bukan cuma lead)?
2. Bauran produk (SAP B1 vs S/4HANA GROW vs Add-on) & industri penopang revenue?
3. Seberapa sehat delivery: on-time go-live, delay, deviasi budget?
4. Apakah support memenuhi SLA? Kategori tiket apa yang mendominasi?
5. Bisakah keterlambatan proyek diprediksi **sejak kickoff**?

## Struktur

```
├── data/raw/              5 tabel relasional (CSV)
├── database/              beone.db (SQLite) + queries.sql (10 query)
├── notebooks/             EDA ter-execute (0 error)
├── dashboard/app.py       Streamlit 5 tab interaktif
├── src/                   generator, db setup, SQL runner, validator, notebook gen
├── docs/                  sumber, data dictionary, executive report
└── outputs/               figure PNG + hasil query CSV
```

## Dataset

| Tabel | Baris | Isi |
|---|---|---|
| `leads` | 2.900 | akuisisi: sumber, industri, kota, produk minat, status |
| `opportunities` | 1.189 | pipeline: produk, **entitas** (BeOne HQ vs sister company PT CORE), nilai deal, hasil, sales cycle |
| `proyek` | 393 | delivery: jadwal vs aktual go-live, budget vs aktual |
| `tiket` | 3.135 | support: kategori, prioritas, jam resolusi, SLA |
| `konsultan` | 36 | dimensi tim: role, level |

Relasi: `leads → opportunities → proyek → tiket` + `konsultan → proyek`.

## Cara menjalankan

```bash
pip install -r requirements.txt
python src/generate_data.py     # generate CSV
python src/db_setup.py          # load ke SQLite
python src/validate_data.py     # 27 data-quality checks
python src/run_sql_analysis.py  # 10 query -> outputs/sql_results/
streamlit run dashboard/app.py  # dashboard
```

## Temuan kunci (fakta → implikasi)

- **Referral & event menang 2-3× win rate** vs telemarketing → realokasi
  budget: cold outreach menghasilkan volume lead tapi bukan deal;
  warm channel adalah *revenue engine* sebenarnya.
- **~35% proyek terlambat**; S/4HANA & modul integrasi paling berisiko →
  delay bukan masalah coding melainkan *scope creep & kesiapan data
  klien* → mitigasi: discovery phase lebih ketat di proyek integrasi.
- **How-to/Training mendominasi tiket** → sinyal klasik under-training
  saat handover → peluang *recurring revenue* (paket training +
  knowledge base) sekaligus menekan beban support.
- **Proyek terlambat → tiket pasca go-live lebih banyak** (cohort
  delivery→support) → kualitas implementasi langsung menentukan
  biaya operasional jangka panjang, bukan cuma reputasi delivery.
- **Delay predictor (RF, AUC ~0.8):** risiko telat bisa diflag sejak
  kickoff — durasi target & level PIC paling menentukan → alokasikan
  PM senior ke proyek berisiko *sebelum* telat, bukan sesudah.

## Skill yang ditunjukkan

Python · pandas/NumPy · SQL (JOIN multi-tabel, FILTER, CTE-style) ·
data quality (27 checks) · EDA + storytelling · uji statistik
(chi-square, ANOVA, effect size) · visualisasi (seaborn/Plotly) ·
dashboard Streamlit · machine learning (Random Forest, ROC-AUC,
threshold tuning) · business metrics B2B (win rate, sales cycle,
pipeline value, SLA, on-time delivery, budget variance, cohort
delivery→support)
