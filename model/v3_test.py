"""v3: probabilistic critical-path model of T_est (relay/fixed sustained mode) under three planning regimes.
T_est = max(T_alert + T_mob, T_access) + T_set   [days]
Anchors from records (Table 3): ad-hoc decision-to-departure 6.5 d, road move 14.2 h, on-site set-up ~7 h incl. recon;
first ground access to the SFP area 6.2 d (17 Mar). Regime parameters other than 'ad hoc' are planning assumptions."""
import json, numpy as np
import analysis as A
rng = np.random.default_rng(42)
N = 20000
tri = lambda a, m, b: rng.triangular(a, m, b, N)
H = 1 / 24
access = tri(3.7, 5.0, 6.2)                 # site access window after explosions/dose-rate peak (assumed)
regimes = {
    "Ad hoc (as recorded)":      dict(alert=tri(5.0, 6.5, 8.0), mob=tri(10 * H, 14.2 * H, 20 * H), setup=tri(4 * H, 7 * H, 12 * H)),
    "Pre-agreed trigger":         dict(alert=tri(0.5, 1.0, 2.0), mob=tri(10 * H, 14.2 * H, 20 * H), setup=tri(4 * H, 7 * H, 12 * H)),
    "Trigger + pre-staged relay": dict(alert=tri(0.5, 1.0, 2.0), mob=tri(2 * H, 3 * H, 5 * H), setup=tri(2 * H, 4 * H, 7 * H)),
}
# deadline samples: U4 no-supply, pool-only (from analysis MC), minus 1-d intermittency margin
Td = []
for s in A.samples:
    A.UNITS["U4"]["T0_C"] = s["T0"]
    r = A.simulate_pool("U4", np.arange(0, 40, A.DT), np.zeros(4000), s["ds"], s["mf"], s["h_af"], s["slosh"], A.T_U4_EXPL, 0.0, s["slosh0"])
    i = np.where(r["w_t"] <= 0)[0]
    Td.append(i[0] * A.DT if len(i) else 40.0)
Td = np.array(Td)
Td_s = rng.choice(Td, N)
out = {"Td": dict(p5=float(np.percentile(Td, 5)), p50=float(np.median(Td)), p95=float(np.percentile(Td, 95)))}
for k, r in regimes.items():
    T = np.maximum(r["alert"] + r["mob"], access) + r["setup"]
    out[k] = dict(p5=float(np.percentile(T, 5)), p50=float(np.median(T)), p95=float(np.percentile(T, 95)),
                  P_meet_Td_minus1=float(np.mean(T <= Td_s - 1.0)), P_meet_Td=float(np.mean(T <= Td_s)),
                  share_access_binding=float(np.mean(access > r["alert"] + r["mob"])),
                  cdf_x=np.sort(T)[::200].tolist())
out["Td_sorted"] = np.sort(Td).tolist()
json.dump(out, open("v3_test.json", "w"), indent=1)
for k, v in out.items():
    if k != "Td_sorted": print(k, {kk: (round(vv, 3) if isinstance(vv, float) else '...') for kk, vv in v.items()})
