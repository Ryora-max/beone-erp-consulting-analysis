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

## `opportunities` (1.189 baris) — pipeline resmi
| Kolom | Tipe | Deskripsi |
|---|---|---|
| id_opportunity | str PK | ID opportunity |
| id_lead | str FK → leads | Lead sumber |
| produk | str | Produk yang ditawarkan |
| nilai_deal_jt | float | Nilai kontrak (Rp juta) |
| hasil | str | Won / Lost |
| tanggal_buat / tanggal_close | date | Periode pipeline |
| sales_cycle_hari | int | Durasi close = close − buat |

## `proyek` (393 baris) — delivery implementasi (dari opp Won)
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

## `tiket` (3.135 baris) — support pasca go-live
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
