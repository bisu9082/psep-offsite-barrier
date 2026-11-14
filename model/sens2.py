"""v2 sensitivity: (a) P_unc vs eta_shuttle (shuttle-only, pool-only); (b) pump-truck clock-time shift; (c) Buncefield duration vs intensity."""
import json, numpy as np
import analysis as A
from data import LOG
out = {}
# (a) eta sweep with other params sampled
etas = np.round(np.arange(0.2, 0.81, 0.05), 2)
S = A.samples[:300]
pa = []
for e in etas:
    H = []
    for s in S:
        s2 = dict(s); s2["eta"] = dict(s["eta"]); s2["eta"]["SHUTTLE"] = float(e)
        H.append(A.run_u4(s2, A.scen["shuttle only (2/day)"]["shift"], A.scen["shuttle only (2/day)"]["log"])["h_m"][A.WIN].min())
    pa.append(float(np.mean(np.array(H) <= 0)))
out["eta_sweep"] = dict(eta=etas.tolist(), p_unc=pa)
# (b) clock-time shift of assumed pump-truck times (entries with 'time assumed')
res_b = {}
for sh_h in (-6, -3, 0, 3, 6):
    log2 = [(u, m, a, t0 + (sh_h / 24 if "assumed" in src else 0), d, tn, src) for (u, m, a, t0, d, tn, src) in LOG]
    H = np.array([A.run_u4(s, None, log2)["h_m"][A.WIN].min() for s in S])
    res_b[str(sh_h)] = dict(p_unc=float(np.mean(H <= 0)), hmin_p50=float(np.median(H)), hmin_p5=float(np.percentile(H, 5)))
out["clock_shift"] = res_b
# (c) Buncefield: plan vs actual foam demand decomposition
plan_rate = 100 * 100 * 8.0          # L/min solution (command planning basis)
plan_conc = plan_rate * 0.03 * 60     # L concentrate for 1 h
window_min = (73.0 - 26.35) * 60
avg_conc = 786_000 / window_min
out["buncefield_demand"] = dict(plan_solution_Lpm=plan_rate, plan_duration_h=1.0, plan_conc_L=plan_conc,
                                actual_conc_L=786_000, window_h=73.0 - 26.35, avg_conc_Lpm=avg_conc,
                                avg_solution_Lpm_at3pct=avg_conc / 0.03, rate_ratio=avg_conc / 0.03 / plan_rate,
                                duration_ratio=(73.0 - 26.35) / 1.0)
json.dump(out, open("sens2.json", "w"), indent=1)
print(json.dumps(out, indent=1))
