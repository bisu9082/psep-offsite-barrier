"""Figures for the PSEP manuscript (static, print). Palette: validated categorical slots 1-4 (light)."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from data import LOG, tf, BUNCEFIELD as B, T_END_F
from barrier import boiloff_tpd, decay_MW

R = json.load(open("results.json"))
C = {"SHUTTLE": "#2a78d6", "RELAY": "#eb6834", "FIXED": "#1baf7a", "HELO": "#eda100"}
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
NAME = {"HELO": "Helicopter drop", "SHUTTLE": "Shuttle (stock-limited)", "RELAY": "Relay (flow-limited)",
        "FIXED": "Fixed / remote (pump truck, FPC)"}
plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
                     "legend.frameon": False, "figure.dpi": 150, "savefig.bbox": "tight", "lines.linewidth": 2})
OUT = "../fig/"


def save(fig, name):
    fig.savefig(OUT + name + ".pdf")
    fig.savefig(OUT + name + ".png", dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------- Fig 1 concept
def fig1():
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    t = np.linspace(0, 14, 1000)
    D = 1.0 * np.exp(-0.01 * t)
    q = np.where(t < 6, 0, np.where(t < 8.5, 0.55, np.where(t < 10.5, 1.6, 1.25)))
    q_sh = np.where((t >= 6) & (t < 8.5), 0.55, 0)
    ax.fill_between(t, 0, q_sh, color=C["SHUTTLE"], alpha=0.25, lw=0, step="post")
    ax.fill_between(t, 0, np.where((t >= 8.5) & (t < 10.5), 1.6, 0), color=C["RELAY"], alpha=0.25, lw=0)
    ax.fill_between(t, 0, np.where(t >= 10.5, 1.25, 0), color=C["FIXED"], alpha=0.25, lw=0)
    ax.plot(t, q, color=INK, lw=1.6, label="Delivered capacity $Q(t)$")
    ax.plot(t, D, color=INK2, lw=1.6, ls="--", label="Demand $D(t)$")
    for x, lab in [(3.0, "no supply"), (7.25, "SHUTTLE\nstock-limited"), (9.5, "RELAY\nflow-limited"), (12.2, "FIXED /\nremote")]:
        ax.text(x, 0.12 if x > 4 else 0.45, lab, ha="center", va="bottom", fontsize=7.5, color=INK)
    ax.axvline(8.5, color=INK2, lw=0.8)
    ax.axvline(13.0, color="#e34948", lw=1.2)
    ax.annotate("", xy=(8.5, 1.85), xytext=(0, 1.85), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.9))
    ax.text(4.25, 1.9, "$T_{est}$: establishment of sustained mode", ha="center", va="bottom", fontsize=7.5, color=INK)
    ax.annotate("", xy=(13.0, 1.55), xytext=(8.5, 1.55), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.9))
    ax.text(10.75, 1.6, "time margin $T_d - T_{est}$", ha="center", va="bottom", fontsize=7.5, color=INK)
    ax.text(13.1, 0.5, "deadline $T_d$\n(fuel uncovered /\nescalation)", fontsize=7, color="#b03030", va="bottom")
    ax.set_xlim(0, 14.8); ax.set_ylim(0, 2.15)
    ax.set_xlabel("Time since initiating event (arbitrary units)")
    ax.set_ylabel("Rate (normalised to demand)")
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.88), fontsize=7.5)
    ax.grid(False)
    save(fig, "fig1_concept")


# ---------------------------------------------------------------- Fig 2 supply log by mode vs demand
def fig2():
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.9), sharex=True)
    off = (14 + 46 / 60) / 24.0                     # t0 at 14:46 -> calendar-day index (0 = 11 Mar)
    days = np.arange(17, 33)                         # 17 Mar .. 1 Apr (32 = 1 Apr)
    modes = ["HELO", "SHUTTLE", "RELAY", "FIXED"]
    for ax, u, P0 in zip(axs, ["U3", "U4"], [0.54, 2.26]):
        present = [m for m in modes if any(e[0] == u and e[1] == m for e in LOG)]
        w = 0.8 / len(present)
        for k, m in enumerate(present):
            v = np.zeros(len(days))
            for e in LOG:
                if e[0] == u and e[1] == m:
                    v[int(np.floor(e[3] + off)) + 11 - days[0]] += e[5]
            x = days + 0.1 + w * k + w / 2
            ax.bar(x[v > 0], v[v > 0], width=w * 0.9, color=C[m], label=NAME[m])
        dem = boiloff_tpd(decay_MW(P0, days - 11 + 0.5 - off))
        ax.step(np.r_[days, days[-1] + 1], np.r_[dem, dem[-1]], where="post", color=INK, lw=1.4, ls="--",
                label="Boil-off demand (100 % retention)")
        ax.set_yscale("log"); ax.set_ylim(10, 5000)
        ax.set_title(f"Unit {u[1]} SFP  ({P0} MW at $t_0$)", fontsize=9, loc="left", color=INK)
        tk = days[::3]
        ax.set_xticks(tk + 0.5); ax.set_xticklabels([str(d) if d <= 31 else f"{d-31} Apr" for d in tk])
        ax.set_xlabel("Calendar day (March 2011)"); ax.set_xlim(days[0], days[-1] + 1)
    axs[0].set_ylabel("Water applied per day (t, log scale)")
    h, l = [], []
    for ax in axs:
        for hh, ll in zip(*ax.get_legend_handles_labels()):
            if ll not in l:
                h.append(hh); l.append(ll)
    fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.12), fontsize=7.5)
    fig.tight_layout()
    save(fig, "fig2_supply_log")


# ---------------------------------------------------------------- Fig 3 U4 inventory trajectories + T_est sensitivity
def fig3():
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw=dict(width_ratios=[1.45, 1]))
    ax = axs[0]
    t = np.array(R["U4_traj_t"])
    sty = [("no supply", INK2, "No supply"), ("shuttle only (2/day)", C["SHUTTLE"], "Shuttle only, 2 sorties/day"),
           ("fixed +4 d", C["RELAY"], "Fixed mode 4 d later"), ("actual", C["FIXED"], "As recorded")]
    for key, col, lab in sty:
        tr = R["U4_traj"][key]
        ax.fill_between(t, tr["p5"], tr["p95"], color=col, alpha=0.15, lw=0)
        ax.plot(t, tr["p50"], color=col, lw=1.8, label=f"{lab}  (P$_{{unc}}$={100*tr['p_uncover']:.1f} %)")
    ax.axhline(0, color="#e34948", lw=1.0)
    ax.axhline(1.5, color=INK, lw=0.9, ls=(0, (4, 2)))
    ax.text(0.3, 1.65, "TEPCO est. minimum, 1.5 m (incl. well inflow)", fontsize=6.6, color=INK)
    ax.text(0.3, -0.6, "top of fuel racks", color="#b03030", fontsize=7)
    for d, lab, ha, dx in [(tf(20, 8, 20), "SDF\nshuttle", "right", -0.15), (tf(22, 17, 17), "pump\ntruck", "left", 0.15)]:
        ax.axvline(d, color=INK2, lw=0.7, ls=":")
        ax.text(d + dx, 7.6, lab, fontsize=6.8, color=INK2, va="top", ha=ha)
    ax.set_ylim(-3, 8); ax.set_xlim(0, t[-1])
    ax.set_xlabel("Days since 11 Mar 2011 14:46"); ax.set_ylabel("Water above fuel (m), pool-only basis")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=6.8)
    ax.set_title("(a) Unit 4 inventory, median and 5–95 % band", fontsize=8.5, loc="left")
    ax = axs[1]
    fd = R["fixed_delay"]
    ax.plot(fd["t_est_d"], fd["p_uncover"], color=C["FIXED"], marker="o", ms=4, lw=1.6, label="Pool-only")
    ax.plot(fd["t_est_d"], fd["p_uncover_coupled"], color=C["SHUTTLE"], marker="s", ms=4, lw=1.6,
            label="With coupled reactor-well volume")
    ax.axhline(0.05, color=INK2, lw=0.8, ls="--"); ax.text(16.1, 0.07, "5 %", fontsize=7, color=INK2, ha="right")
    ax.axvline(fd["t_est_d"][0], color=INK2, lw=0.7, ls=":")
    ax.text(fd["t_est_d"][0] + 0.1, 0.25, "recorded\n22 Mar", fontsize=6.8, color=INK2)
    ax.set_xlabel("Establishment time of fixed mode, $T_{est}$ (d)"); ax.set_ylabel("P(fuel uncovered before 2 Apr)")
    ax.set_ylim(-0.03, 0.75)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), fontsize=6.8)
    ax.set_title("(b) Sensitivity to $T_{est}$", fontsize=8.5, loc="left")
    fig.tight_layout()
    save(fig, "fig3_u4_inventory")


# ---------------------------------------------------------------- Fig 4 design chart
def fig4():
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    dc = R["design_curve"]
    P = np.array(dc["P0_MW"])
    ax.fill_between(P, dc["Td_h6.5"], dc["Td_h7.5"], color=C["SHUTTLE"], alpha=0.18, lw=0)
    ax.plot(P, dc["Td_h7.0"], color=C["SHUTTLE"], lw=1.8, label="Deadline $T_d$ (no make-up; 6.5–7.5 m above fuel)")
    ax.plot(P, np.array(dc["Td_h7.0"]) - 1.0, color=INK2, lw=1.2, ls="--", label="$T_d$ − 1 d margin")
    ob = R["observed_T_est_d"]
    pts = [(0.54, ob["U3 first sortie (shuttle)"], "U3 first sortie", "o"), (0.54, ob["U3 relay"], "U3 relay", "s"),
           (2.26, ob["U4 first sortie (shuttle)"], "U4 first sortie", "o"), (2.26, ob["U4 fixed"], "U4 fixed mode", "s")]
    for x, y, lab, mk in pts:
        ax.plot(x, y, marker=mk, ms=7, color=C["RELAY"], mec=SURF, mew=1.5, ls="none")
        ax.text(x + 0.08, y, lab, fontsize=7, va="center", color=INK)
    ax.set_yscale("log"); ax.set_ylim(3, 150); ax.set_xlim(0.3, 4.0)
    ax.set_yticks([3, 5, 10, 20, 50, 100]); ax.set_yticklabels(["3", "5", "10", "20", "50", "100"])
    ax.set_xlabel("Pool decay heat at $t_0$, $P_0$ (MW)"); ax.set_ylabel("Days since loss of cooling")
    ax.legend(loc="upper right", fontsize=7)
    save(fig, "fig4_design_chart")


# ---------------------------------------------------------------- Fig 5 exposure per tonne
def fig5():
    fig, ax = plt.subplots(figsize=(4.8, 2.1))
    rows = R["exposure"]
    cols = [C["SHUTTLE"], C["RELAY"], C["SHUTTLE"]]
    for i, (r, c) in enumerate(zip(rows, cols)):
        ax.plot([r["per_t_lo"], r["per_t_hi"]], [i, i], color=c, lw=6, solid_capstyle="round")
        ax.text(r["per_t_hi"] * 1.15, i, f"{r['per_t_lo']:.2g}–{r['per_t_hi']:.2g}", va="center", fontsize=7.5, color=INK)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([f"{r['actor']}\n{r['persons']} persons, {r['tonnes']:,} t" for r in rows], fontsize=7.5)
    ax.set_xscale("log"); ax.set_xlim(0.03, 20); ax.invert_yaxis()
    ax.set_xlabel("Collective external dose per tonne applied (person-mSv t$^{-1}$), bounds from binned records")
    ax.grid(axis="y", visible=False)
    save(fig, "fig5_exposure")


# ---------------------------------------------------------------- Fig 6 Buncefield
def fig6():
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    lanes = ["Supply mode", "Foam concentrate", "Water", "Attacks"]
    y = {k: i for i, k in enumerate(lanes)}
    for l, r, col, txt, tc in [(0, 26.35, C["SHUTTLE"], "stock-limited", "white"),
                               (26.35, 73, C["RELAY"], "flow-limited: continuous foam attack", "white"),
                               (73, 102.5, C["FIXED"], "residual", INK)]:
        ax.barh(y["Supply mode"], r - l, left=l, height=0.55, color=col, edgecolor=SURF)
        ax.text((l + r) / 2, y["Supply mode"], txt, ha="center", va="center", fontsize=7, color=tc)
    ax.barh(y["Foam concentrate"], 25.35, left=1, height=0.45, color=GRID, edgecolor=INK2, lw=0.6)
    ax.text(27.3, y["Foam concentrate"], "national stocks mustered (supplier contacted < 1 h); plan 150–300 kL, used 786 kL",
            va="center", fontsize=6.8)
    ax.barh(y["Water"], 2, left=6, height=0.45, color=C["SHUTTLE"], edgecolor="none")
    ax.text(7, y["Water"] + 0.36, "cooling from 1 ML on site,\nwithdrawn after ~2 h", va="top", ha="center", fontsize=6.3)
    ax.barh(y["Water"], 26.35 - 21, left=21, height=0.45, color=GRID, edgecolor=INK2, lw=0.6, hatch="////")
    ax.text(27.3, y["Water"], "1.8–1.9 km HVP relay: > 24 h to establish", va="center", fontsize=6.8)
    for tt, lab in [(11, "aborted"), (15, "one tank\nout"), (26.35, "main attack\n08:22")]:
        ax.plot(tt, y["Attacks"], marker="v", ms=7, color=INK, ls="none")
        if lab == "aborted":
            ax.text(tt - 1.2, y["Attacks"], lab, ha="right", va="center", fontsize=6.3)
        else:
            ax.text(tt + (1.5 if tt == 15 else 0), y["Attacks"] + 0.3, lab, ha="center", va="top", fontsize=6.3)
    ax.text(48, y["Attacks"], "safety withdrawals 12–13 Dec", va="center", fontsize=6.8, color="#b03030")
    for tt, lab in [(0, "explosion"), (26.35, "$T_{est}$ = 26.4 h"), (73, "control"), (102.5, "out")]:
        ax.axvline(tt, color=INK2, lw=0.7, ls=":")
        ax.text(tt, -0.75, lab, ha="center", fontsize=6.8, color=INK2)
    ax.set_yticks(range(len(lanes))); ax.set_yticklabels(lanes)
    ax.set_ylim(len(lanes) - 0.05, -1.0); ax.set_xlim(-2, 106)
    ax.set_xlabel("Hours since 06:01, 11 December 2005"); ax.grid(axis="y", visible=False)
    save(fig, "fig6_buncefield")


# ---------------------------------------------------------------- Fig 7 water fate
def fig7():
    fig, ax = plt.subplots(figsize=(4.8, 1.9))
    a = R["allocation"]["U3"]
    rows = [("Fukushima U3 SFP\n4,833 t applied", a["max_retainable_t"] / a["applied_total"]),
            ("Buncefield\n68 ML applied", B["retention_ML"] / B["water_applied_ML"])]
    lbl = ["at most retainable in pool", "pre-existing retention capacity"]
    for i, (name, f) in enumerate(rows):
        ax.barh(i, f * 100, color=C["FIXED"], height=0.5, edgecolor=SURF)
        ax.barh(i, 100 - f * 100, left=f * 100, color=GRID, height=0.5, edgecolor=SURF)
        ax.text(f * 100 + 1.5, i, f"{f*100:.0f} % {lbl[i]}", va="center", fontsize=7)
    ax.set_yticks([0, 1]); ax.set_yticklabels([r[0] for r in rows], fontsize=7.5)
    ax.set_xlim(0, 100); ax.invert_yaxis(); ax.set_xlabel("Share of applied water (%)"); ax.grid(axis="y", visible=False)
    save(fig, "fig7_water_fate")


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7):
        f()
    print("figures ok")


# ---------------------------------------------------------------- Fig 8 sensitivity + Buncefield demand shape
def fig8():
    S2 = json.load(open("sens2.json"))
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw=dict(width_ratios=[1, 1.15]))
    ax = axs[0]
    e = S2["eta_sweep"]
    ax.plot(e["eta"], e["p_unc"], color=C["SHUTTLE"], marker="o", ms=4, lw=1.8)
    ax.axhline(0.05, color=INK2, lw=0.8, ls="--"); ax.text(0.79, 0.08, "5 %", ha="right", fontsize=7, color=INK2)
    ax.set_xlabel(r"Shuttle hit efficiency $\eta_S$"); ax.set_ylabel("P(fuel uncovered before 2 Apr)")
    ax.set_title("(a) Shuttle-only Unit 4 supply, 2 sorties/day", fontsize=8.5, loc="left")
    ax.set_ylim(-0.03, 1.0)
    ax = axs[1]
    b = S2["buncefield_demand"]
    from matplotlib.patches import Rectangle
    ax.add_patch(Rectangle((0, 0), b["plan_duration_h"], b["plan_solution_Lpm"] / 1000, color=C["SHUTTLE"], alpha=0.85, lw=0))
    ax.add_patch(Rectangle((0, 0), b["window_h"], b["avg_solution_Lpm_at3pct"] / 1000, color=C["RELAY"], alpha=0.85, lw=0))
    ax.text(1.8, 72, "Planning basis: 100 × 100 m at 8 L min$^{-1}$ m$^{-2}$\nfor 1 h → 144 kL concentrate", fontsize=7, va="top")
    ax.text(24, 12.5, "Actual: 786 kL over 46.7 h\n≈ 9,400 L min$^{-1}$ average at 3 %\n(4,700–28,000 at 6–1 %)", fontsize=7, ha="center", va="bottom")
    ax.errorbar([47.8], [b["avg_solution_Lpm_at3pct"] / 1000], yerr=[[b["avg_solution_Lpm_at3pct"] / 2000], [b["avg_solution_Lpm_at3pct"] * 2 / 1000]], fmt="none", ecolor=INK, capsize=3, lw=1)
    ax.set_xlim(0, 50); ax.set_ylim(0, 85)
    ax.set_xlabel("Duration of foam application (h)"); ax.set_ylabel("Foam solution rate (10$^3$ L min$^{-1}$)")
    ax.set_title("(b) Buncefield foam demand: intensity vs duration", fontsize=8.5, loc="left")
    fig.tight_layout()
    save(fig, "fig8_sensitivity_demand")



def fig9():
    T = json.load(open("v3_test.json"))
    fig, ax = plt.subplots(figsize=(6.0, 2.9))
    td = np.array(T["Td_sorted"])
    ax.fill_betweenx([0, 1], np.percentile(td, 5), np.percentile(td, 95), color="#e34948", alpha=0.12, lw=0)
    ax.plot(td, np.linspace(0, 1, len(td)), color="#e34948", lw=1.6, label="Deadline $T_d$, Unit 4 (pool-only)")
    for (k, col, ls) in [("Ad hoc (as recorded)", C["SHUTTLE"], "-"), ("Pre-agreed trigger", C["RELAY"], "-"),
                         ("Trigger + pre-staged relay", C["FIXED"], "--")]:
        x = np.array(T[k]["cdf_x"])
        ax.plot(x, np.linspace(0, 1, len(x)), color=col, lw=1.8, ls=ls, label=f"$T_{{est}}$: {k}")
    ax.axvline(11.10, color=INK2, lw=0.8, ls=":")
    ax.text(11.2, 0.05, "recorded U4\nfixed mode", fontsize=6.8, color=INK2)
    ax.set_xlim(3, 15); ax.set_ylim(0, 1)
    ax.set_xlabel("Days since loss of cooling"); ax.set_ylabel("Cumulative probability")
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=7)
    save(fig, "fig9_test_regimes")


def figA1():
    E = json.load(open("v3_extra.json"))
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.7))
    ax = axs[0]
    for name, col in [("actual", C["FIXED"]), ("shuttle only (2/day)", C["SHUTTLE"])]:
        c = E["convergence"][name]
        ax.plot(c["n"], c["p_unc"], color=col, lw=1.6, marker="o", ms=3, label=f"$P_{{unc}}$, {name}")
    ax.set_xscale("log"); ax.set_xlabel("Number of Monte Carlo runs"); ax.set_ylabel("$P_{unc}$")
    ax.set_title("(a) Convergence", fontsize=8.5, loc="left"); ax.legend(fontsize=6.8)
    ax = axs[1]
    names = list(E["sobol_actual"].keys())
    y = np.arange(len(names))
    for off, (name, col) in zip([-0.18, 0.18], [("actual", C["FIXED"]), ("shuttle only (2/day)", C["SHUTTLE"])]):
        st = [max(E["sobol_" + name][n]["ST"], 0) for n in names]
        ax.barh(y + off, st, height=0.34, color=col, label=name)
    ax.set_yticks(y); ax.set_yticklabels([n.replace("_", " ") for n in names], fontsize=7)
    ax.invert_yaxis(); ax.set_xlabel("Total-order Sobol index (min. level)")
    ax.set_title("(b) Global sensitivity", fontsize=8.5, loc="left"); ax.legend(fontsize=6.8, loc="lower right")
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    save(fig, "figA1_convergence_sobol")


if __name__ == "__main__":
    fig8(); fig9(); figA1()
