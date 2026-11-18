"""Additional figures for the JLPPI version: Arkema case (figC1), cross-case comparison (figX), graphical abstract."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from data import ARKEMA as A, ARKEMA_PRIOR as P
from figures import C, INK, INK2, GRID, save

AR = json.load(open("arkema.json")); X = json.load(open("crosscase.json"))
RED = "#c23b3b"
STOCK, SUST = C["SHUTTLE"], C["FIXED"]


def _tsadt_samples(n=20000):
    rng = np.random.default_rng(20170831)
    u = lambda r: rng.uniform(*r, n)
    K, S, M, cp, Te, dTs = u(P["K_W_m2K"]), u(P["S_m2"]), u(P["M_t"]) * 1e3, u(P["cp_kJ_kgK"]) * 1e3, u(P["Te_C"]), u(P["dT_store_K"])
    sadt = (u(A["sadt_F"]) - 32) / 1.8
    tau = M * cp / (K * S) / 86400
    return tau * np.log((Te - (sadt - dTs)) / (Te - sadt))


def figC1():
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.3, 2.9), gridspec_kw=dict(width_ratios=[2.15, 1], wspace=0.32))
    lanes = ["Warehouse refrigeration\n+ generators", "Liquid-nitrogen backup", "Reefer trailers,\nhigh ground (6)",
             "Reefer trailers,\nstranded (3)", "Off-site sustained\nmode"]
    y = np.arange(len(lanes))[::-1]
    h = 0.5
    ax.barh(y[0], 24 + 3, left=-24, height=h, color=C["FIXED"], alpha=0.35, lw=0)
    ax.barh(y[1], 6 + 24, left=-24, height=h, color=C["FIXED"], alpha=0.35, lw=0)
    ax.barh(y[2], 157.67 + 24, left=-24, height=h, color=STOCK, alpha=0.35, lw=0)
    ax.barh(y[3], 6 + 24, left=-24, height=h, color=STOCK, alpha=0.35, lw=0)
    ax.barh(y[3], 34 - 6, left=6, height=h, color=STOCK, alpha=0.12, lw=0.6, hatch="////", edgecolor=STOCK)
    ax.text(170, y[4], "not established\n(no access; off-site\nstorage needed a\npre-landfall decision)", fontsize=6.5, color=RED, va="center", ha="right")
    for t in A["t_ignition_h"]:
        ax.plot(t, y[3], marker="*", ms=11, color=RED, mec="white", mew=0.5, zorder=5)
    ax.plot(111, y[3] + 0.05, marker="*", ms=11, color=RED, mec="white", mew=0.5, zorder=5)
    ax.plot(157.67, y[2], marker="X", ms=7, color=INK, zorder=5)
    ax.axvline(0, color=INK2, lw=0.8); ax.text(2, -0.5, "site power loss\n28 Aug 02:00", fontsize=6.3, color=INK2, va="bottom", ha="left")
    ax.text(72, y[3] - 0.42, "ignitions", fontsize=6.5, color=RED, ha="left", va="top")
    ax.text(157.67, y[2] + 0.38, "controlled\nburn", fontsize=6.3, color=INK, ha="center", va="bottom")
    ax.set_yticks(y); ax.set_yticklabels(lanes, fontsize=7)
    ax.set_xlim(-26, 172); ax.set_ylim(-0.6, 4.65)
    ax.set_xticks(np.arange(-24, 169, 24)); ax.set_xticklabels([f"{d:g}" for d in np.arange(-1, 8)])
    ax.set_xlabel("Days since site-wide power loss")
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Patch(color=C["FIXED"], alpha=0.35, label="on-site cooling available"),
                       Patch(color=STOCK, alpha=0.35, label="stock-limited mode (reefer)"),
                       Patch(facecolor=STOCK, alpha=0.12, hatch="////", edgecolor=STOCK, label="cooling loss (time uncertain)")],
              fontsize=6.3, loc="upper left", bbox_to_anchor=(-0.02, -0.2), ncol=3)
    ax.set_title("(a) Safety functions and supply modes", fontsize=8, loc="left")
    s = np.sort(_tsadt_samples()); cdf = np.arange(1, s.size + 1) / s.size
    lo, hi = AR["observed_ignition_delay_d"]
    bx.axvspan(lo, hi, color=RED, alpha=0.12, lw=0)
    bx.text(hi + 0.15, 0.08, "recorded\nignition\ndelay", fontsize=6.3, color=RED, ha="left")
    bx.plot(s, cdf, color=INK, lw=1.6)
    bx.axvline(AR["stock_mode_endurance_d"], color=STOCK, lw=1.0, ls="--")
    bx.text(AR["stock_mode_endurance_d"] + 0.2, 0.45, "reefer\nendurance\n(full tank,\n>7 d)", fontsize=6.3, color=STOCK, ha="left")
    bx.set_xlim(0, 10); bx.set_ylim(0, 1)
    bx.set_xlabel("Time from loss of cooling to SADT (d)"); bx.set_ylabel("Cumulative probability")
    bx.set_title("(b) Deadline of stranded trailers", fontsize=8, loc="left")
    save(fig, "figC1_arkema")


def _cross(ax, compact=False):
    names = ["Fukushima Daiichi U4\nspent-fuel pool (2011)", "Buncefield\ntank farm (2005)", "Arkema Crosby\norganic peroxides (2017)"]
    keys = list(X.keys())
    y = [2, 1, 0]
    for yi, k in zip(y, keys):
        c = X[k]
        a, b = max(c["stock_mode"][0], 1.0), c["stock_mode"][1]
        if "stranded_cool_loss" in c:
            b = c["stranded_cool_loss"][0]
            l0, l1 = c["stranded_cool_loss"]
            ax.barh(yi, l1 - l0, left=l0, height=0.36, color=STOCK, alpha=0.12, lw=0.6, hatch="////", edgecolor=STOCK)
        ax.barh(yi, b - a, left=a, height=0.36, color=STOCK, alpha=0.35, lw=0)
        if k.startswith("Buncefield"):
            ax.plot([73.0] * 2, [yi - 0.25, yi + 0.25], color=INK, lw=1.4)
            ax.text(73.0, yi + 0.3, "under\ncontrol", fontsize=6 if compact else 6.4, ha="center", va="bottom", color=INK)
        if c["T_d"]:
            ax.barh(yi, c["T_d"][2] - c["T_d"][0], left=c["T_d"][0], height=0.62, color=RED, alpha=0.13, lw=0)
            ax.plot([c["T_d"][1]] * 2, [yi - 0.31, yi + 0.31], color=RED, lw=1.4)
        if c["T_est"]:
            ax.plot(c["T_est"], yi, marker="D", ms=7 if not compact else 6, color=SUST, mec=INK, mew=0.6, zorder=5)
        else:
            ax.annotate("", xy=(1500, yi), xytext=(400, yi), arrowprops=dict(arrowstyle="->", color=SUST, lw=1.6, ls="--"))
            ax.text(780, yi + 0.22, "no sustained\nmode", fontsize=6 if compact else 6.4, ha="center", va="bottom", color=SUST)
        if "ignitions" in c:
            for t in sorted(set(c["ignitions"])):
                ax.plot(t, yi, marker="*", ms=10, color=RED, mec="white", mew=0.4, zorder=6)
    ax.set_xscale("log"); ax.set_xlim(1, 1600)
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=7 if not compact else 6.3)
    ax.set_ylim(-0.6, 2.6)
    ax.set_xticks([1, 6, 24, 72, 168, 336, 720]); ax.set_xticklabels(["1 h", "6 h", "1 d", "3 d", "7 d", "14 d", "30 d"])
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Time since loss of the safety function (log scale)")


def figX():
    fig, ax = plt.subplots(figsize=(7.0, 2.7))
    _cross(ax)
    verdict = ["met: margin 0.6 d\n(binding: decision)", "delayed: 26.4 h\n(binding: relay set-up)", "failed: not established\n(binding: access, lead time)"]
    for yi, v in zip([2, 1, 0], verdict):
        ax.text(1.03, (yi + 0.6) / 3.2, v, transform=ax.transAxes, fontsize=6.6, va="center", color=INK)
    ax.legend(handles=[Patch(color=STOCK, alpha=0.35, label="stock-limited mode"),
                       plt.Line2D([], [], marker="D", ls="", color=SUST, mec=INK, label="sustained mode established ($T_{est}$)"),
                       Patch(color=RED, alpha=0.13, label="deadline $T_d$ (5-95%; line: median)"),
                       plt.Line2D([], [], marker="*", ls="", color=RED, ms=9, label="ignition")],
              fontsize=6.4, loc="upper center", bbox_to_anchor=(0.45, 1.2), ncol=4)
    save(fig, "figX_crosscase")


def ga():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13.3 / 2.54 * 1.6, 5.0 / 2.54 * 1.6), gridspec_kw=dict(width_ratios=[1, 1.45], wspace=0.55))
    t = np.linspace(0, 14, 600)
    q = np.where(t < 4, 0.0, np.where(t < 8.5, 0.55, 1.4))
    a1.fill_between(t, 0, np.where((t >= 4) & (t < 8.5), 0.55, 0), color=STOCK, alpha=0.3, lw=0)
    a1.fill_between(t, 0, np.where(t >= 8.5, 1.4, 0), color=SUST, alpha=0.3, lw=0)
    a1.plot(t, q, color=INK, lw=1.5); a1.axhline(1.0, color=INK2, ls="--", lw=1.2)
    a1.axvline(11.5, color=RED, lw=1.4)
    a1.text(6.2, 0.62, "stock-\nlimited", ha="center", fontsize=7); a1.text(10.0, 1.48, "sustained", ha="center", fontsize=7)
    a1.text(0.3, 1.05, "demand", fontsize=7, color=INK2); a1.text(11.7, 0.25, "deadline\n$T_d$", fontsize=7, color=RED)
    a1.annotate("", xy=(8.5, 1.78), xytext=(0, 1.78), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.9))
    a1.text(4.25, 1.83, "$T_{est}$", ha="center", fontsize=8)
    a1.set_xlim(0, 14); a1.set_ylim(0, 2.05); a1.set_xticks([]); a1.set_yticks([]); a1.grid(False)
    a1.set_xlabel("time after loss of a safety function", fontsize=7)
    a1.set_title("Barrier check: $T_{est} + \\Delta \\leq T_d$", fontsize=8.5, loc="left")
    _cross(a2, compact=True)
    a2.set_xlabel("time (log scale)", fontsize=7)
    for yi, v, col in zip([2, 1, 0], ["met (0.6 d)", "delayed", "failed"], [SUST, "#c98a00", RED]):
        a2.text(1.02, (yi + 0.6) / 3.2, v, transform=a2.transAxes, fontsize=7.5, va="center", color=col, fontweight="bold")
    fig.savefig("../fig/graphical_abstract.pdf"); fig.savefig("../fig/graphical_abstract.png", dpi=300); fig.savefig("../fig/graphical_abstract.tiff", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    figC1(); figX(); ga()
