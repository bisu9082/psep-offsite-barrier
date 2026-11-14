"""v3: Sobol indices, MC convergence, SDF dose-bin sensitivity."""
import json, numpy as np
from SALib.sample import sobol as ssob
from SALib.analyze import sobol as asob
import analysis as A
from barrier import dose_interval
from data import DOSE_BINS

out = {}
# ---------- Sobol on minimum level (pool-only)
prob = {"num_vars": 7, "names": ["T0", "decay_scale", "h_above_fuel", "slosh_15Mar", "slosh_11Mar", "eta_shuttle", "eta_fixed"],
        "bounds": [[25, 35], [0.8, 1.0], [6.5, 7.5], [0.5, 1.5], [0.3, 0.7], [0.2, 0.8], [0.9, 1.0]]}
X = ssob.sample(prob, 256, calc_second_order=False, seed=7)


def mk(x):
    s = dict(T0=x[0], ds=x[1], h_af=x[2], slosh=x[3], slosh0=x[4],
             eta={"HELO": 0.1, "SHUTTLE": x[5], "RELAY": 0.5, "FIXED": x[6]})
    s["mf"] = A.calib_mass_factor(s["T0"], s["ds"])
    return s


for name in ["actual", "shuttle only (2/day)"]:
    sc = A.scen[name]
    Y = np.array([A.run_u4(mk(x), sc["shift"], sc["log"])["h_m"][A.WIN].min() for x in X])
    Si = asob.analyze(prob, Y, calc_second_order=False, seed=7)
    out["sobol_" + name] = {n: dict(S1=float(a), ST=float(b), ST_conf=float(c))
                            for n, a, b, c in zip(prob["names"], Si["S1"], Si["ST"], Si["ST_conf"])}
# ---------- convergence (2000 samples)
conv = {}
for name in ["actual", "shuttle only (2/day)"]:
    sc = A.scen[name]
    H = np.array([A.run_u4(s, sc["shift"], sc["log"])["h_m"][A.WIN].min() for s in A.samples])
    ns = np.unique(np.round(np.logspace(1.5, np.log10(len(H)), 25)).astype(int))
    conv[name] = dict(n=ns.tolist(), p_unc=[float(np.mean(H[:n] <= 0)) for n in ns],
                      hmin_p50=[float(np.median(H[:n])) for n in ns])
out["convergence"] = conv
# ---------- SDF dose-bin sensitivity
bins, tonnes, n = DOSE_BINS["SDF (shuttle+helo)"]
cases = {"all bins": bins, "excl. 50-100 mSv bin": [b for b in bins if b[1] < 50],
         "excl. >=20 mSv bins": [b for b in bins if b[1] < 20]}
out["sdf_sensitivity"] = {k: dict(zip(["lo", "hi"], [v / tonnes for v in dose_interval(b)])) for k, b in cases.items()}
json.dump(out, open("v3_extra.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "convergence"}, indent=1))
for k, v in conv.items(): print(k, v["p_unc"][-5:], v["hmin_p50"][-3:])
