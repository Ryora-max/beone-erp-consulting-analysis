-- ============================================================
-- Analisis ERP Consulting Performance — PT Beone Optima Solusi
-- Dataset sintetis terkalibrasi konteks publik (bukan data riil)
-- ============================================================

-- Q1. Funnel akuisisi per tahun: lead -> opportunity -> won -> proyek
SELECT l.tahun,
       COUNT(DISTINCT l.id_lead)                        AS leads,
       COUNT(DISTINCT o.id_opportunity)                 AS opportunities,
       COUNT(DISTINCT CASE WHEN o.hasil='Won'
            THEN o.id_opportunity END)                  AS deals_won,
       COUNT(DISTINCT p.id_proyek)                      AS proyek,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN o.hasil='Won'
             THEN o.id_opportunity END)
             / NULLIF(COUNT(DISTINCT o.id_opportunity),0), 1) AS win_rate_pct
FROM leads l
LEFT JOIN opportunities o ON o.id_lead = l.id_lead
LEFT JOIN proyek p       ON p.id_opportunity = o.id_opportunity
GROUP BY l.tahun ORDER BY l.tahun;

-- Q2. Win rate & revenue pipeline per sumber lead
SELECT l.sumber,
       COUNT(*)                                        AS leads,
       COUNT(o.id_opportunity)                         AS pipeline,
       SUM(CASE WHEN o.hasil='Won' THEN 1 ELSE 0 END)  AS won,
       ROUND(100.0*SUM(CASE WHEN o.hasil='Won' THEN 1 ELSE 0 END)
             /NULLIF(COUNT(o.id_opportunity),0),1)     AS win_rate_pct,
       ROUND(SUM(CASE WHEN o.hasil='Won'
             THEN o.nilai_deal_jt END)/1000.0,1)       AS revenue_m
FROM leads l LEFT JOIN opportunities o ON o.id_lead=l.id_lead
GROUP BY l.sumber ORDER BY revenue_m DESC;

-- Q3. Performa per produk: win rate, deal size, sales cycle
SELECT produk,
       COUNT(*) AS opportunities,
       ROUND(100.0*SUM(hasil='Won')/COUNT(*),1)        AS win_rate_pct,
       ROUND(AVG(nilai_deal_jt),0)                     AS avg_deal_jt,
       ROUND(AVG(CASE WHEN hasil='Won'
                 THEN sales_cycle_hari END),0)          AS avg_cycle_won_hari
FROM opportunities
GROUP BY produk ORDER BY avg_deal_jt DESC;

-- Q4. Demand & win rate per industri klien
SELECT l.industri,
       COUNT(*)                        AS leads,
       COUNT(o.id_opportunity)         AS opportunities,
       ROUND(100.0*SUM(o.hasil='Won')
             /NULLIF(COUNT(o.id_opportunity),0),1) AS win_rate_pct
FROM leads l LEFT JOIN opportunities o ON o.id_lead=l.id_lead
GROUP BY l.industri ORDER BY opportunities DESC;

-- Q5. Ketepatan go-live & deviasi budget per produk
SELECT produk,
       COUNT(*) FILTER (WHERE status_proyek!='On Progress') AS proyek_selesai,
       ROUND(100.0*SUM(status_proyek='Go-live Tepat Waktu')
             /NULLIF(COUNT(*) FILTER (WHERE status_proyek!='On Progress'),0),1)
                                                          AS on_time_pct,
       ROUND(AVG(durasi_aktual_hari-durasi_target_hari),1)  AS avg_delay_hari,
       ROUND(100.0*AVG((aktual_jt-budget_jt)/budget_jt),1)  AS avg_budget_deviasi_pct
FROM proyek
GROUP BY produk;

-- Q6. Modul implementasi paling sering + tingkat keterlambatannya
SELECT modul_utama,
       COUNT(*)                                     AS proyek,
       ROUND(100.0*SUM(status_proyek='Go-live Terlambat')
             /NULLIF(COUNT(*) FILTER (WHERE status_proyek!='On Progress'),0),1)
                                                     AS late_pct
FROM proyek
GROUP BY modul_utama ORDER BY proyek DESC;

-- Q7. Performa konsultan: proyek, ketepatan, deviasi budget
SELECT k.id_konsultan, k.role, k.level,
       COUNT(p.id_proyek)                            AS proyek_dipegang,
       ROUND(100.0*SUM(p.status_proyek='Go-live Tepat Waktu')
             /NULLIF(COUNT(*) FILTER (WHERE p.status_proyek!='On Progress'),0),1)
                                                     AS on_time_pct,
       ROUND(100.0*AVG((p.aktual_jt-p.budget_jt)/p.budget_jt),1)
                                                     AS budget_dev_pct
FROM konsultan k LEFT JOIN proyek p ON p.id_konsultan=k.id_konsultan
GROUP BY k.id_konsultan, k.role, k.level
ORDER BY proyek_dipegang DESC;

-- Q8. SLA support per prioritas & kategori tiket
SELECT prioritas,
       COUNT(*)                                AS tiket,
       ROUND(AVG(jam_resolusi),1)              AS avg_jam_resolusi,
       ROUND(100.0*SUM(sla_tercapai)/COUNT(*),1) AS sla_pct
FROM tiket
GROUP BY prioritas
ORDER BY CASE prioritas WHEN 'Critical' THEN 1 WHEN 'High' THEN 2
         WHEN 'Medium' THEN 3 ELSE 4 END;

-- Q9. Beban tiket per industri & produk (kualitas implementasi proxy)
SELECT industri,
       COUNT(*)                                AS tiket,
       COUNT(DISTINCT id_proyek)               AS proyek,
       ROUND(1.0*COUNT(*)/COUNT(DISTINCT id_proyek),1) AS tiket_per_proyek,
       ROUND(100.0*SUM(sla_tercapai)/COUNT(*),1)       AS sla_pct
FROM tiket
GROUP BY industri ORDER BY tiket_per_proyek DESC;

-- Q10. Tren bulanan pipeline & revenue won (12 bulan terakhir)
SELECT strftime('%Y-%m', tanggal_close) AS bulan,
       COUNT(*) FILTER (WHERE hasil='Won')           AS won,
       ROUND(SUM(CASE WHEN hasil='Won'
             THEN nilai_deal_jt END)/1000.0,2)       AS revenue_m
FROM opportunities
GROUP BY bulan ORDER BY bulan;
