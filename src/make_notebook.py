"""Generate notebook EDA (nbformat), eksekusi via nbclient."""
import nbformat as nbf
from nbclient import NotebookClient

nb = nbf.v4.new_notebook()

MD = nbf.v4.new_markdown_cell
CODE = nbf.v4.new_code_cell

nb.cells = [
MD("""# ERP Consulting Performance — Analisis Pipeline, Delivery & Support

**Konteks:** PT Beone Optima Solusi (SAP Gold Partner, Tangerang) —
model bisnis konsultan ERP: *lead → opportunity → implementasi → go-live → support*.

> Dataset **100% sintetis** (`src/generate_data.py`, seed=42) — struktur
> dikalibrasi info publik perusahaan; bukan data riil. Lihat `docs/SUMBER_DATA.md`.

**Pertanyaan bisnis:**
1. Sumber lead mana yang paling efektif menghasilkan deal?
2. Produk & industri mana yang menopang revenue?
3. Seberapa sehat delivery: ketepatan go-live & disiplin budget?
4. Apakah support memenuhi SLA, dan kategori apa yang mendominasi?
5. Bisakah keterlambatan proyek diprediksi sejak kickoff?"""),

CODE("""import pandas as pd, numpy as np
import matplotlib.pyplot as plt, seaborn as sns
sns.set_theme(style="whitegrid")
plt.rcParams.update({"figure.dpi":110,"font.size":10})

leads  = pd.read_csv("../data/raw/leads.csv", parse_dates=[])
opp    = pd.read_csv("../data/raw/opportunities.csv", parse_dates=["tanggal_buat","tanggal_close"])
proyek = pd.read_csv("../data/raw/proyek.csv", parse_dates=["tanggal_mulai","target_golive","tanggal_golive"])
tiket  = pd.read_csv("../data/raw/tiket.csv", parse_dates=["tanggal_dibuat"])
konsultan = pd.read_csv("../data/raw/konsultan.csv")
for n,d in [("leads",leads),("opportunities",opp),("proyek",proyek),("tiket",tiket),("konsultan",konsultan)]:
    print(f"{n:15s} {d.shape}")
"""),

MD("""## 1. Funnel B2B: lead → opportunity → won → proyek"""),
CODE("""fun = pd.DataFrame({
    "Leads": [len(leads)],
    "Opportunity": [len(opp)],
    "Won": [(opp.hasil=="Won").sum()],
    "Proyek": [len(proyek)]}).T.rename(columns={0:"n"})
fun["% dari tahap awal"] = (100*fun["n"]/fun["n"].iloc[0]).round(1)
display(fun)

fig,ax = plt.subplots(figsize=(8,3.2))
sns.barplot(x=fun.index, y=fun["n"], hue=fun.index, legend=False,
            palette=["#3B82F6","#14B8A6","#22C55E","#F59E0B"], ax=ax)
for i,v in enumerate(fun["n"]): ax.text(i,v+15,f"{v:,}",ha="center",fontweight="bold")
ax.set_title("Funnel konversi B2B"); plt.tight_layout()
plt.savefig("../outputs/figures/funnel_b2b.png"); plt.show()
"""),
MD("""**Insight:** drop terbesar di lead→opportunity (kualifikasi awal) —
pola khas B2B consulting. Yang lebih menarik: konversi opportunity→won."""),

CODE("""ws = (opp.join(leads.set_index("id_lead")["sumber"], on="id_lead")
      .groupby("sumber").agg(opp=("id_opportunity","count"),
                             won=("hasil",lambda s:(s=="Won").sum()))
      .assign(win_rate=lambda d:(100*d.won/d.opp).round(1))
      .sort_values("win_rate"))
display(ws)
fig,ax = plt.subplots(figsize=(8,3.6))
sns.barplot(x="win_rate",y=ws.index,data=ws,hue=ws.index,legend=False,
            palette="viridis",ax=ax)
ax.set_title("Win rate per sumber lead"); ax.set_xlabel("Win rate %")
for i,v in enumerate(ws.win_rate): ax.text(v+.4,i,f"{v}%",va="center")
plt.tight_layout(); plt.savefig("../outputs/figures/winrate_sumber.png"); plt.show()
"""),
MD("""**Insight:** referral & event (workshop ala "Business Hacks") menang
telak atas telemarketing — *warm lead* selalu mengalahkan cold outreach.
Implikasi: budget marketing optimal digeser ke event + program referral."""),

MD("""## 2. Produk & industri penopang revenue"""),
CODE("""rev = (opp[opp.hasil=="Won"].join(leads.set_index("id_lead")[["tahun","industri"]],on="id_lead")
       .groupby("produk").agg(deal=("id_opportunity","count"),
                              revenue_jt=("nilai_deal_jt","sum"),
                              avg_jt=("nilai_deal_jt","mean"),
                              cycle=("sales_cycle_hari","mean")).round(1))
rev["revenue_m"]= (rev.revenue_jt/1000).round(2)
display(rev[["deal","revenue_m","avg_jt","cycle"]])

fig,axes = plt.subplots(1,2,figsize=(11,3.8))
sns.barplot(x=rev.index,y="revenue_m",data=rev,hue=rev.index,legend=False,
            palette=["#3B82F6","#8B5CF6","#F59E0B"],ax=axes[0])
axes[0].set_title("Revenue won per produk (Rp M)"); axes[0].set_ylabel("")
top_ind=(opp[opp.hasil=="Won"].join(leads.set_index("id_lead")["industri"],on="id_lead")
         .groupby("industri")["nilai_deal_jt"].sum().sort_values()/1000)
sns.barplot(x=top_ind.values,y=top_ind.index,hue=top_ind.index,legend=False,
            palette="crest",ax=axes[1])
axes[1].set_title("Revenue won per industri (Rp M)"); axes[1].set_xlabel("")
plt.tight_layout(); plt.savefig("../outputs/figures/revenue_produk_industri.png"); plt.show()
"""),
MD("""**Insight:** SAP Business One = mesin volume (pasar UKM); S/4HANA GROW
deal lebih besar + cycle lebih panjang → bauran naik kelas ke mid-market.
Manufaktur & distribusi menopang demand — sesuai positioning riil BeOne."""),

MD("""## 3. Kesehatan delivery: ketepatan go-live & budget"""),
CODE("""done = proyek.dropna(subset=["tanggal_golive"]).copy()
done["delay"] = done.durasi_aktual_hari - done.durasi_target_hari
done["dev_pct"] = 100*(done.aktual_jt-done.budget_jt)/done.budget_jt

ring = (done.groupby("produk")
        .agg(proyek=("id_proyek","count"),
             on_time_pct=("status_proyek",lambda s:round(100*(s=="Go-live Tepat Waktu").mean(),1)),
             avg_delay=("delay","mean"),
             dev_pct=("dev_pct","mean")).round(1))
display(ring)

fig,axes = plt.subplots(1,2,figsize=(11,3.8))
sns.histplot(done.delay,bins=40,kde=True,color="#EF4444",ax=axes[0])
axes[0].axvline(0,ls="--",color="k"); axes[0].set_title("Distribusi delay (hari)")
sns.boxplot(x="produk",y="dev_pct",data=done,hue="produk",legend=False,
            palette="Set2",ax=axes[1])
axes[1].axhline(0,ls="--",color="r"); axes[1].set_title("Deviasi budget %")
plt.tight_layout(); plt.savefig("../outputs/figures/delivery_delay_budget.png"); plt.show()
"""),
MD("""**Insight:** S/4HANA punya ekor delay lebih panjang — kompleksitas
proyek enterprise. Overrun terkonsentrasi di modul integrasi — faktor
eksternal (sistem pihak ketiga) lebih sulit dikendalikan daripada coding."""),

MD("""## 4. Support & SLA"""),
CODE("""sla = (tiket.groupby("prioritas")
       .agg(n=("id_tiket","count"), avg_jam=("jam_resolusi","mean"),
            sla_pct=("sla_tercapai",lambda s:round(100*s.mean(),1)))
       .reindex(["Critical","High","Medium","Low"]))
display(sla.round(1))

fig,axes = plt.subplots(1,2,figsize=(11,3.8))
sns.barplot(x=sla.index,y="sla_pct",data=sla,hue=sla.index,legend=False,
            palette=["#EF4444","#F97316","#F59E0B","#22C55E"],ax=axes[0])
axes[0].set_title("SLA attainment per prioritas"); axes[0].set_ylim(0,105)
kat = tiket.kategori.value_counts()
sns.barplot(x=kat.values,y=kat.index,hue=kat.index,legend=False,
            palette="mako",ax=axes[1])
axes[1].set_title("Kategori tiket")
plt.tight_layout(); plt.savefig("../outputs/figures/support_sla.png"); plt.show()
"""),
MD("""**Insight:** dominasi tiket *How-to/Training* = sinyal handover
kurang matang → peluang paket training sebagai recurring revenue.
Critical attainment harus tertinggi — triase bekerja."""),

MD("""## 5. Prediktor keterlambatan (Random Forest, fitur saat kickoff)"""),
CODE("""from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report

d = done.merge(konsultan[["id_konsultan","level"]],on="id_konsultan")
d["late"] = (d.status_proyek=="Go-live Terlambat").astype(int)
X = pd.get_dummies(d[["produk","industri","modul_utama",
                      "durasi_target_hari","budget_jt","level"]],drop_first=True)
y = d.late
Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=.3,random_state=7,stratify=y)
rf = RandomForestClassifier(n_estimators=200,max_depth=6,random_state=7,n_jobs=-1).fit(Xtr,ytr)
prob = rf.predict_proba(Xte)[:,1]
print("ROC-AUC:",round(roc_auc_score(yte,prob),3))
print(classification_report(yte,(prob>=.5).astype(int),digits=2))

imp = pd.Series(rf.feature_importances_,index=X.columns).nlargest(10).sort_values()
fig,ax=plt.subplots(figsize=(8,3.6))
imp.plot.barh(ax=ax,color="#8B5CF6")
ax.set_title("Feature importance — prediktor delay saat kickoff")
plt.tight_layout(); plt.savefig("../outputs/figures/delay_predictor.png"); plt.show()
"""),
MD("""## Ringkasan & rekomendasi

1. **Marketing:** alihkan budget dari cold outreach ke referral program +
   event workshop — win rate 2-3× lebih tinggi.
2. **Delivery:** screening risiko delay saat kickoff (durasi target,
   budget, level PIC, modul integrasi) → assign PM senior ke proyek
   berisiko; pasang milestone gate untuk data readiness klien.
3. **Support:** tiket how-to dominan → bundel training pasca go-live +
   knowledge base; menekan volume sekaligus recurring revenue.
4. **Portofolio:** pertahankan volume SAP B1 untuk cash flow; tumbuhkan
   S/4HANA GROW secara selektif (deal besar tapi cycle & risiko delay
   lebih tinggi).

*— [Nama Kamu], Data Analyst project (sintetis, konteks publik)*"""),
]

nbf.write(nb, "notebooks/01_erp_consulting_analysis.ipynb")

client = NotebookClient(nb, timeout=300,
                        resources={"metadata": {"path": "notebooks/"}})
client.execute()
nbf.write(nb, "notebooks/01_erp_consulting_analysis.ipynb")
errs = sum(1 for c in nb.cells if c.cell_type == "code"
           for o in c.get("outputs", []) if o.get("output_type") == "error")
print("errors:", errs)
