# Data Dictionary — BeOne ERP Analytics (sintetis)

## `leads` (2.900 baris) — prospek mentah masuk funnel
| Kolom | Tipe | Deskripsi |
|---|---|---|
| id_lead | str PK | ID lead (L00001…) |
| tahun / bulan | int | Waktu lead masuk (2019–2025) |
| sumber | str | Website / Referral Klien / Event·Workshop / Telemarketing / LinkedIn / Partner SAP |
| industri | str | Industri calon klien (8 kategori) |
| kota | str | Kota calon klien (Jabodetabek + Jabar + Jatim) |
| produk_minat | str | SAP Business One / SAP S/4HANA GROW / Add-on & Integrasi |
| status_lead | str | Converted / Lost - no budget / Lost - kompetitor / Cold |

## `opportunities` (1.221 baris) — pipeline resmi
| Kolom | Tipe | Deskripsi |
|---|---|---|
| id_opportunity | str PK | ID opportunity |
| id_lead | str FK → leads | Lead sumber |
| produk | str | Produk yang ditawarkan |
| entitas | str | Entitas penjual: BeOne HQ / PT CORE (sister — hanya SAP B1, mulai 2024) |
| nilai_deal_jt | float | Nilai kontrak (Rp juta) |
| hasil | str | Won / Lost |
| tanggal_buat / tanggal_close | date | Periode pipeline |
| sales_cycle_hari | int | Durasi close = close − buat |

## `proyek` (389 baris) — delivery implementasi (dari opp Won)
| Kolom | Tipe | Deskripsi |
|---|---|---|
| id_proyek | str PK | |
| id_opportunity | str FK → opportunities(Won) | |
| industri / produk / modul_utama | str | Konteks implementasi |
| id_konsultan | str FK → konsultan | PIC delivery |
| tanggal_mulai / target_golive / tanggal_golive | date | Jadwal vs aktual |
| durasi_target_hari / durasi_aktual_hari | int | Delay = aktual − target |
| budget_jt / aktual_jt | float | Biaya direncanakan vs aktual |
| status_proyek | str | Go-live Tepat Waktu / Terlambat / On Progress |

## `tiket` (3.397 baris) — support pasca go-live
| Kolom | Tipe | Deskripsi |
|---|---|---|
| id_tiket | str PK | |
| id_proyek | str FK → proyek | Hanya proyek sudah go-live |
| kategori | str | How-to/Training, Error/Bug, Laporan/Query, Integrasi/Add-on, Akses |
| prioritas | str | Critical / High / Medium / Low |
| tanggal_dibuat | date | |
| jam_resolusi | float | Waktu penyelesaian |
| sla_jam | int | Target SLA per prioritas (8/24/48/96) |
| sla_tercapai | bool | jam_resolusi ≤ sla_jam |

## `konsultan` (36 baris) — dimensi tim
| Kolom | Tipe | Deskripsi |
|---|---|---|
| id_konsultan | str PK | |
| role | str | Functional / Technical Consultant, PM, Support Engineer |
| level | str | Junior / Mid / Senior |
| tahun_gabung | int | |

## Relasi
```
leads 1—n opportunities 1—0..1 proyek 1—n tiket
konsultan 1—n proyek (sebagai PIC)
```

## Asumsi pemodelan (mekanisme yang di-encode di generator)

Data sintetis tidak mengandung "fakta" — ia mengandung **mekanisme yang
sengaja ditetapkan** agar analisis punya sinyal yang bisa diuji. Daftar
lengkapnya, supaya tidak ada temuan yang tampak seperti hasil observasi:

| Mekanisme | Parameter | Dipakai di |
|---|---|---|
| Peluang proyek telat | base 0,28 + produk (S/4HANA +0,14, Add-on +0,10, B1 +0,03, BI −0,02, TSplus −0,10, Training −0,08) + modul kompleks (+0,08) + level PIC (Junior +0,12, Senior −0,10) + durasi target >115% rata-rata produk (+0,08) | `generate_data.py` |
| Beban hypercare | tiket/proyek ~ Poisson(8,5) bila tepat, Poisson(12,5) bila telat (min. 3) | cohort delivery→support |
| Win rate per sumber | Referral > Event > Partner SAP > Website > LinkedIn > Telemarketing | funnel |
| Struktur grup | PT CORE hanya menjual SAP B1, mulai 2024 (±30% deal B1) | analisis entitas |

**Cara membaca temuan:** "pipeline analisis memulihkan efek yang
diasumsikan" adalah klaim yang sah; "BeOne punya efek ini" **bukan**.
Reprodusibilitas: seed 42 + `random_state` turunan; dua kali run
menghasilkan CSV identik.
