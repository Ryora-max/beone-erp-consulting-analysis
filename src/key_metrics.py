"""Hitung metrik kunci dari data -> outputs/key_metrics.md.

Satu sumber kebenaran untuk angka di README / EXECUTIVE_REPORT. Jalankan
ulang setelah regenerasi data, lalu cocokkan dokumen dengan file ini.
"""
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score

leads = pd.read_csv("data/raw/leads.csv")
opp = pd.read_csv("data/raw/opportunities.csv")
pj = pd.read_csv("data/raw/proyek.csv")
tk = pd.read_csv("data/raw/tiket.csv")
kn = pd.read_csv("data/raw/konsultan.csv")

won = opp[opp.hasil == "Won"]
x = opp.merge(leads[["id_lead", "sumber"]], on="id_lead")
wr = x.groupby("sumber").hasil.apply(lambda s: 100 * (s == "Won").mean())
ct = pd.crosstab(x.sumber, x.hasil)
chi2, p_src, *_ = stats.chi2_contingency(ct)
v = np.sqrt(chi2 / (len(x) * (min(ct.shape) - 1)))

done = pj.dropna(subset=["tanggal_golive"]).merge(
    kn[["id_konsultan", "level"]], on="id_konsultan")
late = (done.status_proyek == "Go-live Terlambat")
late_prod = 100 * late.groupby(done.produk).mean()
late_lvl = 100 * late.groupby(done.level).mean()
p_lvl = stats.chi2_contingency(pd.crosstab(done.level, late))[1]

nt = (tk.groupby("id_proyek").size().rename("n").reset_index()
      .merge(done[["id_proyek", "status_proyek"]], on="id_proyek"))
a = nt[nt.status_proyek == "Go-live Terlambat"].n
b = nt[nt.status_proyek == "Go-live Tepat Waktu"].n
p_tk = stats.mannwhitneyu(a, b).pvalue

feats = pd.get_dummies(done[["produk", "modul_utama", "durasi_target_hari",
                             "level"]], drop_first=True).astype(float)
rf = RandomForestClassifier(300, max_depth=3, min_samples_leaf=10,
                            random_state=7, n_jobs=-1)
auc = cross_val_score(rf, feats, late.astype(int),
                      cv=StratifiedKFold(5, shuffle=True, random_state=7),
                      scoring="roc_auc")

mod = done.groupby("modul_utama").status_proyek.agg(
    n="count", late=lambda s: 100 * (s == "Go-live Terlambat").mean()
).query("n >= 8").sort_values("late", ascending=False)

L = [
    "# Key metrics (dihitung otomatis dari data)", "",
    f"- Leads {len(leads):,} | Opportunities {len(opp):,} | Proyek {len(pj):,} "
    f"(selesai {len(done)}) | Tiket {len(tk):,} | Konsultan {len(kn)}",
    f"- Win rate: {100*(opp.hasil=='Won').mean():.1f}%",
    "- Win rate per sumber: " + ", ".join(
        f"{k} {val:.1f}%" for k, val in wr.sort_values().items()),
    f"- Sumber -> win: chi2={chi2:.1f}, p={p_src:.1e}, Cramer's V={v:.2f}",
    "- Volume opp per produk: " + ", ".join(
        f"{k} {val:.1f}%" for k, val in
        (100 * opp.produk.value_counts(normalize=True)).items()),
    "- Median nilai deal Won (Rp jt): " + ", ".join(
        f"{k} {val:.0f}" for k, val in
        won.groupby("produk").nilai_deal_jt.median().items()),
    "- Median sales cycle Won (hari): " + ", ".join(
        f"{k} {val:.0f}" for k, val in
        won.groupby("produk").sales_cycle_hari.median().items()),
    f"- On-time go-live: {100*(~late).mean():.1f}% (n={len(done)})",
    "- % telat per produk: " + ", ".join(
        f"{k} {val:.1f}%" for k, val in late_prod.sort_values().items()),
    "- % telat per level PIC: " + ", ".join(
        f"{k} {val:.1f}%" for k, val in late_lvl.items())
    + f" (chi2 p={p_lvl:.3f})",
    "- Modul paling sering telat (n>=8): " + ", ".join(
        f"{k} {r.late:.0f}% (n={int(r.n)})" for k, r in mod.head(3).iterrows()),
    f"- Overrun budget >3%: "
    f"{100*(((done.aktual_jt-done.budget_jt)/done.budget_jt)>0.03).mean():.1f}%",
    f"- Median tiket/proyek: terlambat {a.median():.0f} vs tepat {b.median():.0f} "
    f"(Mann-Whitney p={p_tk:.1e})",
    f"- SLA attainment: {100*tk.sla_tercapai.mean():.1f}%",
    f"- Delay predictor (RF, 5-fold CV) ROC-AUC: {auc.mean():.2f} +- {auc.std():.2f}",
]
open("outputs/key_metrics.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
