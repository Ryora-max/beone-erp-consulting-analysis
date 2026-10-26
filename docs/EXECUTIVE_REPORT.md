# Executive Report — ERP Consulting Performance

**Konteks:** PT Beone Optima Solusi (SAP Gold Partner) · Dataset sintetis
terkalibrasi konteks publik · 2019–2025

## Ringkasan eksekutif

Bisnis konsultan ERP hidup dari tiga mesin: **pipeline** (lead→deal),
**delivery** (implementasi tepat waktu & budget), dan **support**
(SLA & retensi). Analisis menunjukkan ketiganya punya satu bottleneck
masing-masing — dan semuanya actionable.

## Temuan & rekomendasi

| # | Temuan (evidence) | Rekomendasi |
|---|---|---|
| 1 | Win rate referral/event 2-3× lipat telemarketing (Q2) | Geser budget marketing ke referral program + workshop berkala (model "Business Hacks" bersama vendor) |
| 2 | SAP B1 = 70-80% volume deal; S/4HANA deal 3× lebih besar tapi cycle ~60% lebih panjang (Q3) | Jaga volume B1 untuk cash flow; pipeline S/4HANA perlu forecasting horizon lebih panjang |
| 3 | ~35% proyek terlambat; modul integrasi & S/4HANA paling berisiko (Q5, Q6) | Risk screening saat kickoff + gate "data readiness" klien sebelum build; buffer eksplisit untuk integrasi pihak ketiga |
| 4 | ~28% proyek overrun budget (Q5) | Estimasi ulang untuk modul integrasi; change-request process yang disiplin |
| 5 | How-to/Training = kategori tiket terbesar (Q8) | Bundel paket training pasca go-live + knowledge base self-service → recurring revenue & tiket turun |
| 6 | Delivery terkonsentrasi di sedikit konsultan senior (Q7) | Pairing junior-senior, dokumentasi runbook, kurangi knowledge silo |

## Metrik kunci

- Pipeline → Won conversion: ~37% (win rate pipeline)
- On-time go-live: ~65%
- SLA attainment: ~87%
- Sales cycle median: ~105 hari (B1), ~170 hari (S/4HANA)

## Metodologi singkat

- **Data**: 2.900 leads + 1.189 opportunities + 393 proyek + 3.135 tiket
  + 36 konsultan (5 tabel relasional, SQLite).
- **Analisis**: funnel & cohort deskriptif, SQL multi-join, Random Forest
  untuk prediktor delay (fitur saat kickoff), forecast OLS.
- **Reproducibility**: generator ber-seed, 24 data-quality checks lolos,
  notebook ter-execute 0 error.
- **Batasan**: seluruh data sintetis — parameter adalah asumsi skenario,
  bukan angka riil perusahaan.
