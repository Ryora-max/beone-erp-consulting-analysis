# Sumber & Pemodelan Data — BeOne ERP Analytics

> ⚠️ **Dataset 100% sintetis.** Seluruh baris digenerate programatik
> (`src/generate_data.py`, seed=42). Struktur bisnisnya dimodelkan dari
> informasi publik di bawah; **tidak ada satu pun angka riil perusahaan
> yang digunakan**. Proyek ini tidak berafiliasi dengan PT Beone Optima
> Solusi dan tidak merepresentasikan data, klien, pendapatan, atau
> kinerja aktualnya.

## Sumber publik yang dipakai untuk konteks

| Aspek yang dikalibrasi | Sumber |
|---|---|
| Profil bisnis: SAP Gold Partner, layanan end-to-end (consulting, implementasi, kustomisasi, integrasi, migrasi, training, managed support) | https://www.sap.com/partners/profile/pt-beone-optima-solusi-beone-solution |
| Produk utama: SAP Business One, SAP S/4HANA GROW | https://beonesolution.com/ + profil SAP di atas |
| Modul SAP Business One (Financials, Sales, Purchasing, Inventory, Production, Reporting) | https://beonesolution.com/modul-modul-sap-business-one-yang-sering-digunakan/ |
| Modul Manufacturing S/4HANA GROW (MRP, scheduling, capacity) | https://beonesolution.com/modul-manufacturing-di-sap-s-4hana-grow-public-edition/ |
| Industri klien: manufaktur, distribusi, retail, pertambangan, konstruksi, jasa profesional (+F&B, agrikultur dari situs/Jobstreet) | profil SAP + https://beonesolution.com/sap-business-one-adalah/ |
| Proses lead-gen: telemarketing → appointment → meeting business consultant | Lowongan Telemarketing Intern di Glints |
| Aktivitas marketing: workshop "Business Hacks" bersama SAP Indonesia (Okt 2022) | https://wartaekonomi.co.id/read466359/ + https://www.marketeers.com/respons-revolusi-4-0-beone-optima-solusi-tawarkan-solusi-erp-dari-sap/ |
| Add-on: Coretax, Plant Maintenance, integrasi ARD | https://beonesolution.com/sap-business-one-solusi-erp-terintegrasi/ + knowledge base Freshdesk BeOne |
| Skala perusahaan: puluhan karyawan (Jobstreet 11–50, Glints 51–200), kantor Tangerang | https://id.jobstreet.com/companies/beone-optima-beone-solution-168549704476218 + situs resmi |
| **Sister company PT Cipta Optima Ragam Era (CORE)** — badan hukum terpisah berbisnis identik (implementasi & support SAP B1), berdiri ~Okt 2023, personel bersama: Managing Partner BeOne jadi Komisaris CORE; beberapa konsultan pindah BeOne→CORE | LinkedIn (profil Cahyo Sugiarto, Daniel Febriano, Redia Veronika) + coretechindonesia.com |
| **Business Insight** produk in-house (seller App Store = PT Beone Optima Solusi) | https://apps.apple.com/ (listing "BOS Business Insight") + katalog beonesolution.com |
| **TSplus** distributor resmi Indonesia | https://beonesolution.com/reseller-tsplus-remote-access/ |
| Model sales area (Jabar, Kalimantan) — bukan kantor cabang; cabang Bandung & Batam pernah disebut 2014 (tak terverifikasi kini) | posting rekrutmen LinkedIn + laporan UMN 2014 |

## Parameter skenario (asumsi, BUKAN fakta perusahaan)

Tidak ada data publik untuk angka-angka ini — ditetapkan sebagai parameter
realistis industri konsultan ERP UKM:

| Parameter | Nilai simulasi | Catatan |
|---|---|---|
| Win rate pipeline | ~25-35% per sumber (referral tertinggi, telemarketing terendah) | pola umum B2B: warm > cold |
| Nilai deal | B1: median ~Rp300 jt; S/4HANA: ~Rp900 jt; Add-on: ~Rp110 jt | distribusi lognormal |
| Sales cycle | B1 ~105 hari; S/4HANA ~170 hari; Add-on ~60 hari | ERP = keputusan multi-stakeholder |
| Proyek terlambat | ~35% | benchmark literatur implementasi ERP (40-60% late umum dilaporkan) |
| Budget overrun | ~28% proyek | scope creep & data readiness |
| SLA attainment | ~85% | target umum managed support |
| Hypercare spike | ~60% tiket muncul ≤90 hari pasca go-live | pola umum pasca-implementasi |

## Batasan & etika

- Nama klien nyata (mis. testimoni di situs BeOne) **tidak dipakai** —
  industri saja yang diabstraksikan.
- Angka "500+ projects / 50+ team" dari company profile tidak diverifikasi
  independen → tidak dijadikan basis volume data.
- Klaim "first implementor in Asia" tidak terverifikasi → tidak dipakai.
- **"Be One Solutions" (grup Swiss, beonesolutions.com) BUKAN afiliasi** —
  kemiripan nama kebetulan; tidak dimodelkan.
- **myECO** hampir pasti produk pihak ketiga (startup Tangsel/Malang
  terpisah) yang dipasarkan ulang — tidak dimodelkan sebagai produk
  in-house.
- Relasi korporat formal BeOne↔CORE (kepemilikan saham) belum
  terdokumentasi publik — dimodelkan sebagai "sister company" berdasarkan
  bukti personel bersama, bukan klaim legal.

## Lihat juga

- `docs/PROFIL_BEONE.md` — timeline legal 2012-2026, struktur grup
  (CORE, Xpertise Academy, Gooday Cloud, BMOlsson), partner vendor,
  klien terverifikasi, relasi kampus.
- `docs/ANALISIS_KONEKSI.md` — analisis kemungkinan koneksi BeOne-POLINDRA.
