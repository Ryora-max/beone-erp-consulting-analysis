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

> Seluruh angka dihitung otomatis (`python src/key_metrics.py` →
> `outputs/key_metrics.md`). Mekanisme di balik data adalah **asumsi
> pemodelan** (`docs/DATA_DICTIONARY.md`) — yang ditunjukkan di sini adalah
> kemampuan analisis memulihkan & mengkuantifikasinya, bukan kinerja
> nyata BeOne.

- **Referral Klien 53,5% & Event 38,0% vs Telemarketing 17,1%** (3,1× / 2,2×;
  χ² p=1e-12, Cramér's V=0,23) → realokasi budget dari cold outreach ke
  warm channel.
- **S/4HANA = 12% volume tapi 25% revenue won** (deal median 2,5× B1,
  cycle +72%) → B1 menjaga cash flow, S/4HANA butuh forecast horizon panjang.
- **40,1% proyek terlambat** — S/4HANA 50%, Add-on & Integrasi 46,5%,
  modul Purchasing 57%; PIC Junior 44,6% vs Mid 33,1% (p=0,046, signifikan
  tipis) → risk screening saat kickoff + data-readiness gate.
- **Proyek terlambat → median 12 tiket vs 8** (p=6e-22) → anggarkan
  hypercare lebih besar bila go-live slip; kualitas delivery menentukan
  biaya support.
- **How-to/Training = 29,8% tiket** → peluang paket training + knowledge
  base (recurring revenue, tiket turun).
- **Delay predictor: ROC-AUC 0,62 ± 0,06 (5-fold CV)** — sinyal moderat,
  layak untuk *triase* bukan keputusan tunggal. Evaluasi memakai CV karena
  hanya ±340 proyek selesai; satu split bisa menyesatkan (split tunggal
  sebelumnya memberi AUC 0,39 — di bawah acak — murni karena n_test=101).

## Skill yang ditunjukkan

Python · pandas/NumPy · SQL (JOIN multi-tabel, FILTER, CTE-style) ·
data quality (27 checks) · EDA + storytelling · uji statistik
(chi-square, ANOVA, effect size) · visualisasi (seaborn/Plotly) ·
dashboard Streamlit · machine learning (Random Forest, ROC-AUC,
threshold tuning) · business metrics B2B (win rate, sales cycle,
pipeline value, SLA, on-time delivery, budget variance, cohort
delivery→support)
