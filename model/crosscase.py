"""Cross-case summary (Fukushima U4, Buncefield, Arkema Crosby). Times in hours since loss of the safety function.
Writes crosscase.json used by figures_jlppi.py and the manuscript table."""
import json
R = json.load(open("results.json")); A = json.load(open("arkema.json"))
D = 24.0
cases = {
    "Fukushima Daiichi U4 SFP (2011)": dict(
        t0="loss of pool cooling, 11 Mar 2011 14:46",
        stock_mode=[R["observed_T_est_d"]["U4 first sortie (shuttle)"] * D, R["observed_T_est_d"]["U4 fixed"] * D],
        T_est=R["observed_T_est_d"]["U4 fixed"] * D,
        T_d=[R["U4_deadline_d"]["p5"] * D, R["U4_deadline_d"]["p50"] * D, R["U4_deadline_d"]["p95"] * D],
        outcome="fuel not uncovered; P_unc 1.5% (pool-only)", verdict="met, margin 0.6 d",
        binding="decision and allocation of a mode able to reach the pool"),
    "Buncefield tank farm (2005)": dict(
        t0="explosion, 11 Dec 2005 06:01",
        stock_mode=[6.0, 26.35], T_est=26.35, T_d=None,
        outcome="fire under control 73 h, out 102.5 h", verdict="delayed; escalation present at t0",
        binding="set-up of a 1.8-1.9 km water relay (>24 h)"),
    "Arkema Crosby (2017)": dict(
        t0="site-wide power loss, 28 Aug 2017 02:00",
        stock_mode=[-24.0, 157.67],
        stranded_cool_loss=[6.0, 34.0],
        T_est=None,
        T_d=[6.0 + A["t_SADT_d"]["p5"] * D, 20.0 + A["t_SADT_d"]["p50"] * D, 34.0 + A["t_SADT_d"]["p95"] * D],
        ignitions=[72.0, 111.0, 111.0], controlled_burn=157.67,
        outcome="3 stranded trailers ignited; 6 burned in a controlled burn", verdict="failed; no sustained mode",
        binding="site access and decision lead time for off-site storage (days to weeks)"),
}
json.dump(cases, open("crosscase.json", "w"), indent=1)
for k, v in cases.items():
    print(k, {kk: (round(x, 1) if isinstance(x, float) else x) for kk, x in v.items() if kk in ("T_est", "T_d", "verdict")})
