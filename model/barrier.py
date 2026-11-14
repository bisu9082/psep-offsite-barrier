"""Off-site mitigation barrier model: demand, supply modes, inventory margin, exposure accounting."""
import numpy as np
from data import POOL, UNITS, DECAY_LAMBDA_PER_D, LOG, ETA, T_END_F, DOSE_BINS

CP = 4.186e-3      # MJ/(kg K)
HFG = 2.257        # MJ/kg
RHO = 958.0        # kg/m3 at 100 C
DAY = 86400.0


def decay_MW(P0, t_d, scale=1.0):
    return scale * P0 * np.exp(-DECAY_LAMBDA_PER_D * t_d)


def boiloff_tpd(P_MW):
    return P_MW * DAY / HFG / 1000.0  # t/day


def supply_series(unit, t, eta=None, modes=None, log=LOG, shift_d=None):
    """Mass delivered [t] per time step for unit; eta: dict mode->efficiency (default 1)."""
    dt = t[1] - t[0]
    s = np.zeros_like(t)
    for u, mode, actor, t0, dur_h, tonnes, _ in log:
        if u != unit or (modes and mode not in modes):
            continue
        t_start = t0 if shift_d is None else shift_d(mode, t0)
        if t_start is None:
            continue
        d = max(dur_h / 24.0, dt)
        mask = (t >= t_start) & (t < t_start + d)
        if not mask.any():
            mask[np.searchsorted(t, t_start)] = True
        e = 1.0 if eta is None else eta.get(mode, 1.0)
        s[mask] += e * tonnes / mask.sum()
    return s


def simulate_pool(unit, t, supply_t, decay_scale=1.0, mass_factor=1.0, h_af=None, slosh_m=0.0, t_slosh=None, extra_t=0.0, slosh0_m=0.0):
    """Lumped SFP model. Returns dict with T [C], water above fuel [m], overflow [t] (cumulative)."""
    p = UNITS[unit]
    A = POOL["area_m2"]
    h_af = POOL["h_above_fuel_m"] if h_af is None else h_af
    m_full = POOL["volume_m3"] * 1000.0                 # kg (nominal)
    m_eff = mass_factor * m_full                         # thermal mass incl. coupled volumes
    w_full = h_af * A * RHO / 1000.0 + extra_t           # t of water above fuel when full (+coupled well inventory)
    dt = (t[1] - t[0]) * DAY
    T = p["T0_C"]
    w = w_full - slosh0_m * A * RHO / 1000.0           # earthquake sloshing at t0
    out_T, out_w, out_over = [], [], []
    over = 0.0
    slosh_done = t_slosh is None
    for i, ti in enumerate(t):
        if not slosh_done and ti >= t_slosh:
            w -= slosh_m * A * RHO / 1000.0
            slosh_done = True
        P = decay_MW(p["P0_MW"], ti, decay_scale) * 1e6  # W
        if T < 100.0:
            T += P * dt / (m_eff * CP * 1e6)
            T = min(T, 100.0)
            evap = 0.0
        else:
            evap = P * dt / (HFG * 1e6) / 1000.0          # t
        w += supply_t[i] - evap
        if w > w_full:
            over += w - w_full
            w = w_full
        out_T.append(T)
        out_w.append(w)
        out_over.append(over)
    w = np.array(out_w)
    return dict(T=np.array(out_T), w_t=w, h_m=w * 1000.0 / RHO / A, overflow_t=np.array(out_over), w_full=w_full)


def time_to_uncover(unit, decay_scale=1.0, mass_factor=1.0, h_af=None, slosh_m=0.0, t_slosh=None, t_max=40.0):
    t = np.arange(0, t_max, 0.01)
    r = simulate_pool(unit, t, np.zeros_like(t), decay_scale, mass_factor, h_af, slosh_m, t_slosh)
    idx = np.where(r["w_t"] <= 0)[0]
    return t[idx[0]] if len(idx) else np.inf, r


def shuttle_capacity(n_veh, tank_t, cycles_per_day, eta):
    return n_veh * tank_t * cycles_per_day * eta  # t/day retained


def min_fleet(demand_tpd, tank_t, cycles_per_day, eta):
    return demand_tpd / (tank_t * cycles_per_day * eta)


def dose_interval(bins):
    lo = sum(n * a for n, a, b in bins)
    hi = sum(n * b for n, a, b in bins)
    return lo, hi


def exposure_table():
    rows = []
    for actor, (bins, tonnes, n) in DOSE_BINS.items():
        lo, hi = dose_interval(bins)
        rows.append(dict(actor=actor, persons=n, tonnes=tonnes, coll_lo=lo, coll_hi=hi,
                         per_t_lo=lo / tonnes, per_t_hi=hi / tonnes))
    return rows
