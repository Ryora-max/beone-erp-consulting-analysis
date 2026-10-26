"""Validasi kualitas data: kelengkapan, rentang nilai, integritas relasional,
konsistensi logika bisnis."""
import pandas as pd

leads = pd.read_csv("data/raw/leads.csv")
opp = pd.read_csv("data/raw/opportunities.csv")
proyek = pd.read_csv("data/raw/proyek.csv")
tiket = pd.read_csv("data/raw/tiket.csv")
konsultan = pd.read_csv("data/raw/konsultan.csv")

hasil = []

def check(nama, kondisi, detail=""):
    hasil.append((kondisi, f"{nama} {detail}".strip()))

# ---- kelengkapan ----
check("leads tidak kosong", len(leads) > 0)
check("tidak ada null di kolom kunci leads",
      leads[["id_lead", "tahun", "sumber", "status_lead"]].notna().all().all())
check("id_lead unik", leads["id_lead"].is_unique)
check("id_opportunity unik", opp["id_opportunity"].is_unique)
check("id_proyek unik", proyek["id_proyek"].is_unique)
check("id_tiket unik", tiket["id_tiket"].is_unique)

# ---- rentang nilai ----
check("tahun lead dalam 2019-2025",
      leads["tahun"].between(2019, 2025).all())
check("bulan lead 1-12", leads["bulan"].between(1, 12).all())
check("nilai deal positif", (opp["nilai_deal_jt"] > 0).all())
check("sales cycle positif", (opp["sales_cycle_hari"] > 0).all())
check("budget positif", (proyek["budget_jt"] > 0).all())
check("jam resolusi positif", (tiket["jam_resolusi"] > 0).all())
check("hasil opp hanya Won/Lost", opp["hasil"].isin(["Won", "Lost"]).all())
check("prioritas valid",
      tiket["prioritas"].isin(["Critical", "High", "Medium", "Low"]).all())

# ---- integritas relasional ----
check("semua opp.id_lead ada di leads",
      opp["id_lead"].isin(set(leads["id_lead"])).all())
check("semua proyek.id_opportunity ada di opp Won",
      proyek["id_opportunity"].isin(
          set(opp.loc[opp.hasil == "Won", "id_opportunity"])).all())
check("semua tiket.id_proyek ada di proyek",
      tiket["id_proyek"].isin(set(proyek["id_proyek"])).all())
check("semua proyek.id_konsultan ada di konsultan",
      proyek["id_konsultan"].isin(set(konsultan["id_konsultan"])).all())

# ---- logika bisnis ----
check("opp Won selalu berasal dari lead Converted",
      opp.merge(leads, on="id_lead")
      .pipe(lambda d: (d.loc[d.hasil == "Won", "status_lead"]
                       == "Converted").all()))
done = proyek.dropna(subset=["tanggal_golive"])
check("proyek selesai punya durasi aktual",
      done["durasi_aktual_hari"].notna().all())
check("durasi aktual >= 0.5 * target",
      (done["durasi_aktual_hari"] >= 0.5 * done["durasi_target_hari"]).all())
check("tiket muncul setelah go-live",
      tiket.merge(proyek[["id_proyek", "tanggal_golive"]], on="id_proyek")
      .pipe(lambda d: (pd.to_datetime(d.tanggal_dibuat)
                       >= pd.to_datetime(d.tanggal_golive)).all()))
check("SLA konsisten dengan flag",
      ((tiket["jam_resolusi"] <= tiket["sla_jam"]) == tiket["sla_tercapai"]).all())
check("status proyek valid",
      proyek["status_proyek"].isin(
          ["Go-live Tepat Waktu", "Go-live Terlambat", "On Progress"]).all())
# entitas CORE baru beroperasi 2024+ dan hanya pegang SAP B1
_e = opp.merge(leads[["id_lead", "tahun"]], on="id_lead")
check("entitas valid",
      opp["entitas"].isin(["BeOne HQ", "PT CORE (sister)"]).all())
check("CORE hanya menangani SAP B1",
      (_e.loc[_e.entitas == "PT CORE (sister)", "produk"]
       == "SAP Business One").all())
check("CORE belum ada sebelum 2024",
      (_e.loc[_e.entitas == "PT CORE (sister)", "tahun"] >= 2024).all())

gagal = [n for ok, n in hasil if not ok]
for ok, n in hasil:
    print(("[OK]  " if ok else "[FAIL]") + " " + n)
print(f"\n{len(hasil)-len(gagal)}/{len(hasil)} checks lolos")
if gagal:
    raise SystemExit(1)
