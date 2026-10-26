# Executive Report — ERP Consulting Performance

**Konteks:** PT Beone Optima Solusi (SAP Gold Partner) · Dataset **sintetis**
terkalibrasi konteks publik · 2019–2025
**Sumber angka:** `outputs/key_metrics.md` (dihitung otomatis oleh `src/key_metrics.py`)

## Ringkasan eksekutif

Bisnis konsultan ERP hidup dari tiga mesin: **pipeline** (lead→deal),
**delivery** (implementasi tepat waktu & budget), dan **support**
(SLA & beban hypercare). Masing-masing punya satu bottleneck yang jelas dan
dapat ditindaklanjuti. Seluruh angka di bawah berasal dari data sintetis —
mekanisme yang diuji adalah *asumsi pemodelan* (lihat `DATA_DICTIONARY.md`),
bukan fakta operasional perusahaan.

## Temuan & rekomendasi

| # | Temuan (evidence) | Rekomendasi |
|---|---|---|
| 1 | Win rate **Referral Klien 53,5%** dan **Event/Workshop 38,0%** vs **Telemarketing 17,1%** (3,1× dan 2,2×); sumber→win signifikan, χ²=64,5, p=1e-12, Cramér's V=0,23 (efek sedang) | Geser budget dari cold outreach ke program referral + workshop berkala; evaluasi telemarketing sebagai kualifikasi awal, bukan penutup deal |
| 2 | SAP B1 = **63,6%** volume opportunity dan **67,9%** revenue won; S/4HANA GROW hanya 12,0% volume tapi **25,3%** revenue — median deal **2,5×** lebih besar (Rp764 jt vs Rp304 jt) dengan sales cycle **+72%** (186 vs 108 hari) | Jaga B1 untuk cash flow; forecast pipeline S/4HANA dengan horizon lebih panjang |
| 3 | **40,1%** proyek terlambat (on-time 59,9%, n=337). Paling sering terlambat: S/4HANA GROW **50%**, Add-on & Integrasi **46,5%**; modul **Purchasing 57%**, Inventory 50%, WMS 50%. Produk ringan (TSplus, Training) hanya 13–14% | Risk screening saat kickoff + gate "data readiness" klien; buffer eksplisit untuk S/4HANA & integrasi |
| 4 | PIC **Junior terlambat 44,6%** vs **Mid 33,1%** (χ² p=0,046 — signifikan tipis, bukan kuat) | Pairing junior–senior di proyek berisiko; jangan simpulkan kausalitas dari satu uji |
| 5 | **26,1%** proyek overrun budget >3% | Disiplin change-request; estimasi ulang modul berisiko tinggi |
| 6 | Proyek terlambat menghasilkan **median 12 tiket** vs **8** pada proyek tepat waktu (Mann-Whitney p=6e-22) | Anggarkan hypercare lebih besar untuk proyek yang slip; pakai sebagai KPI kualitas delivery. *Catatan: hubungan ini diasumsikan di generator — pipeline berhasil memulihkannya* |
| 7 | **How-to/Training = 29,8%** tiket (kategori terbesar); SLA tercapai **88,5%** (Critical 89,9%, merata antar prioritas) | Bundel paket training + knowledge base → recurring revenue sekaligus menekan tiket |

## Model prediktif — apa yang boleh & tidak boleh diklaim

Delay predictor (Random Forest, fitur saat kickoff: produk, modul, durasi
target, level PIC) mencapai **ROC-AUC 0,62 ± 0,06 (5-fold CV)**. Artinya
**sinyal ada tetapi moderat** — layak sebagai alat *triase* untuk memilih
proyek yang perlu pengawalan ekstra, tidak layak sebagai keputusan tunggal.
Dengan hanya ~340 proyek selesai, evaluasi memakai cross-validation (bukan
satu split) agar angka tidak ditentukan oleh keberuntungan pembagian data.

## Metrik kunci

- Win rate pipeline: 35,6% (1.221 opportunity)
- On-time go-live: 59,9% · SLA attainment: 88,5%
- Median sales cycle Won: B1 108 hari · S/4HANA 186 hari
- PT CORE (sister company, sejak 2024): 27 proyek Won, Rp8,1 M vs BeOne HQ Rp137,6 M

## Metodologi

- **Data:** 2.900 leads + 1.221 opportunities + 389 proyek + 3.397 tiket
  + 36 konsultan (5 tabel relasional, SQLite). Generator ber-seed dan
  **terbukti reprodusibel** (hash CSV identik antar-run).
- **Analisis:** funnel & cohort deskriptif, SQL multi-join (11 query),
  uji inferensial (χ², Welch t, ANOVA, Mann-Whitney, logit OR), Random
  Forest dengan CV, forecast OLS.
- **Validasi:** 27 data-quality checks lolos; notebook ter-execute 0 error.
- **Batasan:** seluruh data sintetis. Efek (mis. S/4HANA lebih berisiko,
  junior lebih sering telat) adalah *asumsi* yang di-encode; yang
  ditunjukkan project ini adalah kemampuan pipeline analisis memulihkan
  dan mengkuantifikasinya secara jujur, termasuk menyatakan ketika sinyalnya
  lemah.
