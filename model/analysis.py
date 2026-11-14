"""Case A (Fukushima SFP) and Case B (Buncefield) analyses. Writes results.json used by figures and manuscript."""
import json
import numpy as np
from data import LOG, ETA, UNITS, POOL, tf, T_END_F, SHUTTLE_PF, BUNCEFIELD as B
from barrier import (simulate_pool, supply_series, decay_MW, boiloff_tpd, time_to_uncover, CP,
                     exposure_table, min_fleet, shuttle_capacity, DAY)

rng = np.random.default_rng(20111311)
N = 2000
DT = 0.01
t = np.arange(0, 30.0, DT)
T84 = tf(14, 4, 8)            # U4 pool 84 C at 13 Mar 19:08 UTC (IAEA update 18 Mar 2011)
T_U4_EXPL = tf(15, 6, 0)      # Unit 4 building explosion ~06:00 15 Mar


def calib_mass_factor(T0, ds, P0=2.26):
    tt = np.linspace(0, T84, 2000)
    E = np.trapezoid(decay_MW(P0, tt, ds) * 1e6, tt * DAY)
    return E / (CP * 1e6 * POOL["volume_m3"] * 1000.0 * (84.0 - T0))


def sample():
    s = dict(T0=rng.uniform(25, 35), ds=rng.uniform(0.8, 1.0), h_af=rng.uniform(6.5, 7.5),
             slosh=rng.uniform(0.5, 1.5), slosh0=rng.uniform(0.3, 0.7),  # TEPCO est. 1.0 m (15 Mar) and 0.5 m (11 Mar), via NAS 2016
             eta={m: rng.uniform(*r) for m, r in ETA.items()})
    s["mf"] = calib_mass_factor(s["T0"], s["ds"])
    return s


WIN = t <= T_END_F


def run_u4(s, shift=None, log=LOG, coupled=False):
    UNITS["U4"]["T0_C"] = s["T0"]
    sup = supply_series("U4", t, s["eta"], log=log, shift_d=shift)
    extra = (s["mf"] - 1.0) * POOL["volume_m3"] if coupled else 0.0
    return simulate_pool("U4", t, sup, s["ds"], s["mf"], s["h_af"], s["slosh"], T_U4_EXPL, extra, s["slosh0"])


res = {}
# ---------------------------------------------------------------- A1 deadline without supply
samples = [sample() for _ in range(N)]
tu = []
for s in samples:
    UNITS["U4"]["T0_C"] = s["T0"]
    r = simulate_pool("U4", np.arange(0, 40, DT), np.zeros(4000), s["ds"], s["mf"], s["h_af"], s["slosh"], T_U4_EXPL, 0.0, s["slosh0"])
    i = np.where(r["w_t"] <= 0)[0]
    tu.append(i[0] * DT if len(i) else np.inf)
tu = np.array(tu)
mf = np.array([s["mf"] for s in samples])
res["U4_deadline_d"] = dict(p5=float(np.percentile(tu, 5)), p50=float(np.median(tu)), p95=float(np.percentile(tu, 95)))
res["U4_mass_factor"] = dict(p5=float(np.percentile(mf, 5)), p50=float(np.median(mf)), p95=float(np.percentile(mf, 95)))
UNITS["U4"]["T0_C"] = 27.0
res["U4_deadline_nominal_pool_only_d"] = float(time_to_uncover("U4")[0])
res["boiloff_tpd"] = {u: boiloff_tpd(UNITS[u]["P0_MW"]) for u in UNITS}

# ---------------------------------------------------------------- A2 reconstruction (actual log) + counterfactuals
def shift_fixed(delta):
    def f(mode, t0):
        return t0 + delta if mode == "FIXED" else t0
    return f


def no_fixed_shuttle_continues(mode, t0):
    return None if mode == "FIXED" else t0


# shuttle-only counterfactual: SDF continues two 80-t sorties/day from 20 Mar until end
LOG_SHUTTLE = [e for e in LOG if not (e[0] == "U4" and e[1] == "FIXED")]
d = tf(21, 18, 0)
while d < 30:
    LOG_SHUTTLE.append(("U4", "SHUTTLE", "SDF", d, 1.3, 80, "counterfactual"))
    d += 0.5

scen = {"actual": dict(shift=None, log=LOG), "no supply": dict(shift=lambda m, t0: None, log=LOG),
        "shuttle only (2/day)": dict(shift=None, log=LOG_SHUTTLE)}
for dd in [2, 4]:
    scen[f"fixed +{dd} d"] = dict(shift=shift_fixed(dd), log=LOG)
traj = {}
for coupled in (False, True):
    for name, sc in scen.items():
        H = np.array([run_u4(s, sc["shift"], sc["log"], coupled)["h_m"][WIN] for s in samples[:400]])
        key = name + (" | coupled" if coupled else "")
        traj[key] = dict(p5=np.percentile(H, 5, axis=0)[::5].tolist(), p50=np.median(H, axis=0)[::5].tolist(),
                         p95=np.percentile(H, 95, axis=0)[::5].tolist(),
                         p_uncover=float(np.mean(H.min(axis=1) <= 0)), hmin_p50=float(np.median(H.min(axis=1))),
                         hmin_p5=float(np.percentile(H.min(axis=1), 5)))
res["U4_traj_t"] = t[WIN][::5].tolist()
res["U4_traj"] = traj

# critical delay of sustained (FIXED) mode: P(uncover) vs delay
delays = np.arange(0, 5.01, 0.25)
fd = dict(delay_d=delays.tolist(), t_est_d=(tf(22, 17, 17) + delays).tolist())
for coupled in (False, True):
    pu = []
    for dd in delays:
        H = np.array([run_u4(s, shift_fixed(dd), LOG, coupled)["h_m"][WIN].min() for s in samples[:300]])
        pu.append(float(np.mean(H <= 0)))
    fd["p_uncover_coupled" if coupled else "p_uncover"] = pu
res["fixed_delay"] = fd

# ---------------------------------------------------------------- A3 allocation U3 vs U4 (applied vs demand)
alloc = {}
for u in ["U3", "U4"]:
    applied = {m: sum(e[5] for e in LOG if e[0] == u and e[1] == m) for m in ["HELO", "SHUTTLE", "RELAY", "FIXED"]}
    tt = np.arange(tf(17, 0, 0), T_END_F, DT)
    dem = float(np.sum(boiloff_tpd(decay_MW(UNITS[u]["P0_MW"], tt))) * DT)
    alloc[u] = dict(applied=applied, applied_total=sum(applied.values()), boiloff_17Mar_1Apr=dem,
                    pool_capacity_above_fuel_t=POOL["h_above_fuel_m"] * POOL["area_m2"] * 0.958)
    alloc[u]["max_retainable_t"] = dem + alloc[u]["pool_capacity_above_fuel_t"]
    alloc[u]["min_not_retained_t"] = max(0.0, alloc[u]["applied_total"] - alloc[u]["max_retainable_t"])
res["allocation"] = alloc

# ---------------------------------------------------------------- A4 shuttle sizing
D4 = boiloff_tpd(decay_MW(2.26, tf(20, 12, 0)))
res["shuttle"] = dict(
    demand_U4_20Mar_tpd=D4,
    capacity_range_tpd=[shuttle_capacity(10, 6, 1, 0.2), shuttle_capacity(13, 8, 2, 0.8)],
    observed_SDF_U4_tpd=[160.0, 90.0],
    min_fleet_eta={str(e): {str(c): min_fleet(D4, 7.0, c, e) for c in [1, 2]} for e in [0.2, 0.35, 0.5, 0.8]},
)

# ---------------------------------------------------------------- A5 exposure intervals
res["exposure"] = exposure_table()

# ---------------------------------------------------------------- B Buncefield
res["buncefield"] = dict(
    t_first_attack_h=11.0, t_second_attack_h=15.0, t_main_attack_h=26.35, t_water_ge_h=24.0,
    t_control_h=73.0, t_out_h=102.5,
    foam_ratio_used_to_plan=B["foam_used_L"] / B["foam_plan_L"],
    foam_ratio_used_to_doubled=B["foam_used_L"] / B["foam_plan_doubled_L"],
    water_not_retained_ML=B["water_applied_ML"] - B["retention_ML"],
    retention_fraction=B["retention_ML"] / B["water_applied_ML"],
    onsite_water_fraction=1.0 / B["water_applied_ML"],
    window_h=73.0 - 26.35,
)
# ---------------------------------------------------------------- design curve: deadline vs decay heat (pool-only, no supply)
P0s = np.linspace(0.3, 4.0, 38)
dc = {"P0_MW": P0s.tolist()}
for h in (6.5, 7.0, 7.5):
    vals = []
    for P0 in P0s:
        UNITS["X"] = dict(P0_MW=float(P0), T0_C=30.0)
        tu_, _ = time_to_uncover("X", 1.0, 1.0, h, t_max=120.0)
        vals.append(float(tu_))
    dc[f"Td_h{h}"] = vals
res["design_curve"] = dc
res["observed_T_est_d"] = {"U3 first sortie (shuttle)": tf(17, 19, 5), "U3 relay": tf(19, 0, 30),
                           "U4 first sortie (shuttle)": tf(20, 8, 20), "U4 fixed": tf(22, 17, 17)}
json.dump(res, open("results.json", "w"), indent=1, default=float)
for k, v in res.items():
    if k not in ("U4_traj", "U4_traj_t"):
        print(k, v)
for k, v in traj.items():
    print(k, "P(uncover)=", v["p_uncover"], "hmin50=", round(v["hmin_p50"], 2))
