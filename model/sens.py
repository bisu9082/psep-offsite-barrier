"""Sensitivity: which uncertain inputs drive minimum inventory (Spearman), by scenario."""
import json, numpy as np
from scipy.stats import spearmanr
import analysis as A   # re-runs main analysis (results.json refreshed)
out = {}
for name, sc in [("shuttle only (2/day)", A.scen["shuttle only (2/day)"]), ("fixed +4 d", A.scen["fixed +4 d"])]:
    S = A.samples[:400]
    hmin = np.array([A.run_u4(s, sc["shift"], sc["log"])["h_m"][A.WIN].min() for s in S])
    X = {"eta_shuttle": [s["eta"]["SHUTTLE"] for s in S], "eta_fixed": [s["eta"]["FIXED"] for s in S],
         "decay_scale": [s["ds"] for s in S], "h_above_fuel": [s["h_af"] for s in S], "slosh": [s["slosh"] for s in S],
         "T0": [s["T0"] for s in S], "mass_factor": [s["mf"] for s in S]}
    out[name] = {k: float(spearmanr(v, hmin)[0]) for k, v in X.items()}
    es = np.array(X["eta_shuttle"])
    out[name]["P_unc_by_eta_shuttle"] = {f"{lo:.1f}-{hi:.1f}": float(np.mean(hmin[(es >= lo) & (es < hi)] <= 0))
                                          for lo, hi in [(0.2, 0.4), (0.4, 0.6), (0.6, 0.8)]}
json.dump(out, open("sens.json", "w"), indent=1)
print(json.dumps(out, indent=1))
