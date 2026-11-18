"""Case C (Arkema Crosby 2017): deadline check for a SADT-limited inventory after loss of refrigeration.

Lumped heat-up of trailer contents with no internal heat generation (self-heating below SADT neglected):
    M cp dT/dt = K S (Te - T)  ->  t_SADT = tau * ln[(Te - T0)/(Te - T_SADT)],  tau = M cp / (K S)
Neglecting self-heating and internal temperature gradients lengthens t_SADT for the first effect and shortens it
for the second; the result is a planning-grade estimate, compared with the recorded ignition delay as a check.
Writes arkema.json.
"""
import json
import numpy as np
from data import ARKEMA as A, ARKEMA_PRIOR as P

rng = np.random.default_rng(20170831)
N = 20000
u = lambda r: rng.uniform(*r, N)
K, S, M, cp, Te, dTs = u(P["K_W_m2K"]), u(P["S_m2"]), u(P["M_t"]) * 1e3, u(P["cp_kJ_kgK"]) * 1e3, u(P["Te_C"]), u(P["dT_store_K"])
sadt = (u(A["sadt_F"]) - 32.0) / 1.8
T0 = sadt - dTs
tau_d = M * cp / (K * S) / 86400.0
ok = Te > sadt
t_sadt = np.full(N, np.inf)
t_sadt[ok] = tau_d[ok] * np.log((Te[ok] - T0[ok]) / (Te[ok] - sadt[ok]))

lo_obs = (A["t_ignition_h"][0] - A["t_cool_loss_h"][1]) / 24.0   # earliest ignition after latest cooling loss
hi_obs = (A["t_ignition_h"][1] - A["t_cool_loss_h"][0]) / 24.0   # latest ignition after earliest cooling loss
fin = t_sadt[np.isfinite(t_sadt)]
res = dict(
    N=N, frac_Te_above_SADT=float(ok.mean()),
    tau_d=dict(p5=float(np.percentile(tau_d, 5)), p50=float(np.median(tau_d)), p95=float(np.percentile(tau_d, 95))),
    t_SADT_d=dict(p5=float(np.percentile(fin, 5)), p50=float(np.median(fin)), p95=float(np.percentile(fin, 95))),
    observed_ignition_delay_d=[lo_obs, hi_obs],
    frac_t_SADT_le_obs_hi=float(np.mean(t_sadt <= hi_obs)),
    frac_t_SADT_le_obs_lo=float(np.mean(t_sadt <= lo_obs)),
    sadt_C=[(A["sadt_F"][0] - 32) / 1.8, (A["sadt_F"][1] - 32) / 1.8],
    deadline_from_last_power_d=(A["t_ignition_h"][0] - 3.0) / 24.0,
    stock_mode_endurance_d=A["trailer_endurance_full_tank_d"],
    T_est_sustained="not established",
)
json.dump(res, open("arkema.json", "w"), indent=1)
for k, v in res.items():
    print(k, v)
