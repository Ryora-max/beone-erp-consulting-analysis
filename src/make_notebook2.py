"""Generate notebook 02: uji statistik + model delay + cohort retention."""
import nbformat as nbf
from nbclient import NotebookClient

nb = nbf.v4.new_notebook()
MD, CODE = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell

nb.cells = [
MD("""# Statistik Inferensial & Model Delay — BeOne ERP Analytics

Notebook kedua: dari *deskriptif* ke *inferensial* — uji hipotesis +
effect size + pemodelan, plus cohort analysis delivery→support.

> Dataset sintetis (seed=42), konteks publik BeOne. Lihat docs/SUMBER_DATA.md"""),

CODE("""import pandas as pd, numpy as np
import matplotlib.pyplot as plt, seaborn as sns
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
sns.set_theme(style="whitegrid"); plt.rcParams.update({"figure.dpi":110,"font.size":10})

leads=pd.read_csv("../data/raw/leads.csv")
opp=pd.read_csv("../data/raw/opportunities.csv",parse_dates=["tanggal_buat","tanggal_close"])
proyek=pd.read_csv("../data/raw/proyek.csv",parse_dates=["tanggal_mulai","target_golive","tanggal_golive"])
tiket=pd.read_csv("../data/raw/tiket.csv",parse_dates=["tanggal_dibuat"])
konsultan=pd.read_csv("../data/raw/konsultan.csv")

def cramers_v(tab):
    chi2=stats.chi2_contingency(tab)[0]
    n=tab.values.sum(); r,c=tab.shape
    return np.sqrt(chi2/(n*min(r-1,c-1)))

def chi2_uji(df,faktor,target):
    tab=pd.crosstab(df[faktor],df[target])
    chi2,p,_,_=stats.chi2_contingency(tab)
    return chi2,p,cramers_v(tab)
"""),

MD("""## 1. Apakah sumber lead memengaruhi kemenangan deal? (chi-square)

H0: hasil deal independen dari sumber lead."""),
CODE("""d = opp.join(leads.set_index("id_lead")["sumber"],on="id_lead")
d["won"] = (d.hasil=="Won").astype(int)
tab = pd.crosstab(d.sumber, d.won)
chi2,p,v = chi2_uji(d,"sumber","won")
print(tab); print(f"chi2={chi2:.1f}, p={p:.2e}, Cramér's V={v:.3f}")
print("\\nWin rate per sumber (%):")
print((100*tab[1]/tab.sum(axis=1)).round(1).sort_values(ascending=False))
"""),
MD("""**Baca:** p sangat kecil → dependen (sumber memang memengaruhi hasil).
Yang lebih penting adalah **effect size** (Cramér's V pada output di atas;
≈0,1 kecil, ≈0,3 sedang) — bukan sekadar "signifikan karena n besar"."""),

MD("""## 2. Sales cycle deal Won vs Lost (t-test + effect size)"""),
CODE("""w = d.loc[d.won==1,"sales_cycle_hari"]; l = d.loc[d.won==0,"sales_cycle_hari"]
t,p = stats.ttest_ind(w,l,equal_var=False)
cohen = (w.mean()-l.mean())/np.sqrt((w.var()+l.var())/2)
print(f"Won: mean={w.mean():.0f}hr (n={len(w)}), Lost: mean={l.mean():.0f}hr (n={len(l)})")
print(f"t={t:.2f}, p={p:.3f}, Cohen's d={cohen:.3f}")
fig,ax=plt.subplots(figsize=(8,3.4))
sns.kdeplot(w,fill=True,label="Won",color="#22C55E",ax=ax)
sns.kdeplot(l,fill=True,label="Lost",color="#EF4444",ax=ax)
ax.set_title("Distribusi sales cycle: Won vs Lost"); ax.legend()
plt.tight_layout(); plt.savefig("../outputs/figures/cycle_won_lost.png"); plt.show()
"""),

MD("""## 3. Delay per produk (ANOVA)"""),
CODE("""done = proyek.dropna(subset=["tanggal_golive"]).copy()
done["delay"]=done.durasi_aktual_hari-done.durasi_target_hari
grup=[g.delay.values for _,g in done.groupby("produk") if len(g)>10]
F,p = stats.f_oneway(*grup)
print(f"ANOVA delay ~ produk: F={F:.1f}, p={p:.3f}")
print(done.groupby("produk")["delay"].agg(["mean","std","count"]).round(1))
"""),

MD("""## 4. Cohort: apakah proyek terlambat menghasilkan lebih banyak tiket?

Ini menghubungkan **delivery → support burden** — pertanyaan bisnis nyata:
apakah go-live yang telat berarti implementasi buruk (tiket banyak)?

> Catatan metodologi: data sintetis — hubungan ini **diasumsikan** di
> generator (hypercare lebih berat pada proyek telat). Notebook menguji
> apakah pipeline analisis *memulihkan* efek tersebut dengan benar,
> bukan menemukan fakta tentang perusahaan nyata."""),
CODE("""coh = (tiket.groupby("id_proyek").size().rename("n_tiket").reset_index()
       .merge(done[["id_proyek","status_proyek","delay","produk"]],on="id_proyek"))
coh["late"]=(coh.status_proyek=="Go-live Terlambat").astype(int)
a=coh.loc[coh.late==1,"n_tiket"]; b=coh.loc[coh.late==0,"n_tiket"]
t,p = stats.mannwhitneyu(a,b,alternative="two-sided")
print(f"Tiket/proyek — Terlambat: median={a.median():.0f} (n={len(a)}), "
      f"Tepat waktu: median={b.median():.0f} (n={len(b)})")
print(f"Mann-Whitney U p={p:.4f}")
r = coh.delay.corr(coh.n_tiket)
print(f"Korelasi delay vs jumlah tiket: r={r:.3f}")
fig,ax=plt.subplots(figsize=(8,3.6))
sns.boxplot(x="late",y="n_tiket",data=coh,hue="late",legend=False,
            palette=["#22C55E","#EF4444"],ax=ax)
ax.set_xticklabels(["Tepat waktu","Terlambat"])
ax.set_title("Beban tiket pasca go-live: proyek telat vs tepat")
plt.tight_layout(); plt.savefig("../outputs/figures/delay_vs_tickets.png"); plt.show()
"""),

MD("""## 5. Model delay saat kickoff — regresi logistik (odds ratio)"""),
CODE("""d2 = done.merge(konsultan[["id_konsultan","level"]],on="id_konsultan")
d2["late"]=(d2.status_proyek=="Go-live Terlambat").astype(int)
mod = smf.logit("late ~ durasi_target_hari + budget_jt + "
                "C(produk) + C(level)", data=d2).fit(disp=0)
ortab = pd.DataFrame({"OR":np.exp(mod.params),
                      "lo":np.exp(mod.conf_int()[0]),
                      "hi":np.exp(mod.conf_int()[1]),
                      "p":mod.pvalues}).round(3)
display(ortab.sort_values("OR",ascending=False))

fig,ax=plt.subplots(figsize=(8,3.8))
o = ortab.drop("Intercept").sort_values("OR")
ax.errorbar(o.OR,range(len(o)),xerr=[o.OR-o.lo,o.hi-o.OR],fmt="o",
            color="#8B5CF6",ecolor="#C4B5FD",capsize=4)
ax.axvline(1,ls="--",color="gray"); ax.set_yticks(range(len(o)),o.index)
ax.set_title("Odds ratio keterlambatan (95% CI) — >1 = menaikkan risiko")
plt.tight_layout(); plt.savefig("../outputs/figures/odds_delay.png"); plt.show()
"""),
MD("""**Baca:** OR>1 = risiko telat naik; OR<1 = protektif. CI yang tidak
menyentuh 1 = signifikan di 95%. Perhatikan *lebar CI*: dengan ±340
proyek selesai, banyak faktor punya CI lebar — sinyal ada, presisinya
terbatas. Interpretasikan arah & besar efek, bukan hanya p-value."""),

MD("""## Ringkasan inferensial

| Pertanyaan | Uji | Hasil |
|---|---|---|
| Sumber → win? | chi-square + V | signifikan, efek moderat |
| Cycle Won vs Lost beda? | Welch t-test + Cohen's d | (lihat output) |
| Delay beda per produk? | ANOVA | (lihat output) |
| Proyek telat → tiket lebih banyak? | Mann-Whitney + korelasi | (lihat output) |
| Prediktor delay saat kickoff? | Logistic OR (95% CI) | (lihat output) |

*— [Nama Kamu], Data Analyst project*"""),
]

nbf.write(nb, "notebooks/02_statistik_dan_model_delay.ipynb")
nb = nbf.read("notebooks/02_statistik_dan_model_delay.ipynb", as_version=4)
client = NotebookClient(nb, timeout=300,
                        resources={"metadata": {"path": "notebooks/"}})
client.execute()
nbf.write(nb, "notebooks/02_statistik_dan_model_delay.ipynb")
errs = sum(1 for c in nb.cells if c.cell_type == "code"
           for o in c.get("outputs", []) if o.get("output_type") == "error")
print("errors:", errs)
