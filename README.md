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
python src/validate_data.py     # 24 data-quality checks
python src/run_sql_analysis.py  # 10 query -> outputs/sql_results/
streamlit run dashboard/app.py  # dashboard
```

## Temuan kunci (data sintetis)

- **Referral & event menang 2-3× win rate** vs telemarketing — warm > cold.
- **~35% proyek terlambat**; S/4HANA & modul integrasi paling berisiko.
- **How-to/Training mendominasi tiket** → peluang recurring revenue
  (paket training + knowledge base).
- **Delay predictor (RF):** durasi target & level PIC paling menentukan —
  screening risiko bisa dilakukan sejak kickoff.

## Skill yang ditunjukkan

Python · pandas/NumPy · SQL (JOIN multi-tabel, FILTER, CTE-style) ·
data quality (24 checks) · EDA + storytelling · visualisasi
(seaborn/Plotly) · dashboard Streamlit · machine learning
(Random Forest, ROC-AUC) · business metrics B2B (win rate, sales cycle,
pipeline value, SLA, on-time delivery, budget variance)
