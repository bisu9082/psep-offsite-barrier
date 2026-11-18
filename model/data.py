"""Public-record inputs for the two cases. Every number carries a source key (see notes 03/04/06).
Times: Fukushima in days since 2011-03-11 14:46 JST (t=0); Buncefield in hours since 2005-12-11 06:01 (t=0).
"""
from datetime import datetime

T0_F = datetime(2011, 3, 11, 14, 46)


def tf(d, hh=12, mm=0, mon=3):
    """day-of-month + clock time -> days since t0 (Fukushima)."""
    return (datetime(2011, mon, d, hh, mm) - T0_F).total_seconds() / 86400.0


# ---------------------------------------------------------------- Fukushima SFP (Units 3, 4)
POOL = dict(
    area_m2=9.9 * 12.2,       # pool plan area (TEPCO; IAEA 2015 TV1)
    volume_m3=1390.0,         # total pool volume [IAEA 2015]
    h_above_fuel_m=7.0,       # nominal water above rack top (range 6.5-7.5 assumed)
)
UNITS = {
    # decay heat at t0 [MW] (TEPCO Miyata 2012; IAEA 2015 s1.3.3.1); U4 1.58 MW at 90 d (Yanagi 2012)
    "U3": dict(P0_MW=0.54, T0_C=30.0),
    "U4": dict(P0_MW=2.26, T0_C=27.0),
}
DECAY_LAMBDA_PER_D = 0.00397  # ln(2.26/1.58)/90 (Yanagi et al. 2012)

# Supply log: (unit, mode, actor, start[d], duration[h], tonnes, source)
# modes: HELO, SHUTTLE (stock-limited sorties), RELAY (flow-limited continuous), FIXED (pump truck / FPC line)
LOG = [
    ("U3", "HELO", "SDF", tf(17, 9, 48), 0.2, 30, "MOD WP2011; NISA28"),
    ("U3", "SHUTTLE", "Police", tf(17, 19, 5), 0.13, 44, "NPA; RC129-5-1"),
    ("U3", "SHUTTLE", "SDF", tf(17, 19, 35), 0.57, 30, "HQ report; NISA67"),
    ("U3", "SHUTTLE", "SDF", tf(18, 14, 0), 0.63, 40, "HQ report"),
    ("U3", "SHUTTLE", "TEPCO", tf(18, 14, 42), 0.1, 2, "HQ report"),
    ("U3", "RELAY", "Fire", tf(19, 0, 30), 0.33, 60, "FDMA; RC129-5-2"),
    ("U3", "RELAY", "Fire", tf(19, 14, 5), 13.58, 2430, "FDMA; RC129-5-2"),
    ("U4", "SHUTTLE", "SDF", tf(20, 8, 20), 1.15, 80, "HQ report; NERHQ85"),
    ("U4", "SHUTTLE", "SDF", tf(20, 18, 22), 1.35, 80, "HQ report; NERHQ85"),
    ("U3", "RELAY", "Fire", tf(20, 21, 30), 6.47, 1137, "FDMA; RC129-5-2"),
    ("U4", "SHUTTLE", "SDF", tf(21, 6, 37), 2.07, 90, "MOD 3/21; NERHQ85"),
    ("U3", "RELAY", "Fire", tf(22, 15, 10), 0.83, 150, "FDMA; RC129-5-2"),
    ("U4", "FIXED", "TEPCO", tf(22, 17, 17), 3.25, 150, "NISA67"),
    ("U3", "FIXED", "TEPCO", tf(23, 11, 0), 2.0, 35, "NISA67 (FPC line; time assumed)"),
    ("U4", "FIXED", "TEPCO", tf(23, 10, 0), 3.0, 130, "NISA67 (time assumed)"),
    ("U3", "FIXED", "TEPCO", tf(24, 5, 0), 5.0, 120, "NISA67 (FPC; time assumed)"),
    ("U4", "FIXED", "TEPCO", tf(24, 14, 0), 3.0, 150, "NISA67 (time assumed)"),
    ("U3", "RELAY", "Fire", tf(25, 13, 30), 2.5, 450, "FDMA; RC129-5-2"),
    ("U4", "FIXED", "TEPCO", tf(25, 19, 0), 3.0, 150, "NISA67 (time assumed)"),
    ("U3", "FIXED", "TEPCO", tf(27, 12, 0), 2.0, 100, "NISA67 (time assumed)"),
    ("U4", "FIXED", "TEPCO", tf(27, 16, 0), 3.0, 125, "NISA67 (time assumed)"),
    ("U3", "FIXED", "TEPCO", tf(29, 14, 0), 2.0, 100, "NISA67 (time assumed)"),
    ("U4", "FIXED", "TEPCO", tf(30, 14, 0), 3.0, 140, "NISA67 (time assumed)"),
    ("U3", "FIXED", "TEPCO", tf(31, 14, 0), 2.0, 105, "NISA67 (time assumed)"),
    ("U4", "FIXED", "TEPCO", tf(1, 14, 0, mon=4), 3.5, 180, "NISA67 (time assumed)"),
]
T_END_F = tf(2, 0, 0, mon=4)

# Hit efficiency priors (fraction of applied water retained in the pool). No measured values exist;
# ranges are assumptions bounded by geometry (open roof, spray from ground) and are varied in MC.
ETA = {"HELO": (0.02, 0.3), "SHUTTLE": (0.2, 0.8), "RELAY": (0.2, 0.8), "FIXED": (0.9, 1.0)}

# Shuttle planning factors (SDF): engines 5-13, tank 6-8 t (per-engine water by day), cycle 8-11 h
SHUTTLE_PF = dict(n_veh=(10, 13), tank_t=(6.0, 8.0), cycles_per_day=(1.0, 2.0))

# Exposure: binned public dose records (UNSCEAR 2013 Annex A s123, s140-142 & Table 9; RC129-5-1/2/3)
DOSE_BINS = {
    # actor: (list of (n persons, lo mSv, hi mSv), tonnes delivered by actor, persons)
    "SDF (shuttle+helo)": ([(132, 0, 10), (3, 10, 20), (8, 20, 50), (4, 50, 100)], 340 + 30, 147),  # MOD official engine total ~340 t + helicopter 30 t
    "Fire (relay)": ([(1, 29.8, 29.8), (16, 10, 20), (232, 0, 10)], 4227, 249),
    "Police (shuttle)": ([(1, 10, 10), (12, 0, 10)], 44, 13),
}

# ---------------------------------------------------------------- Buncefield (hours since 06:01 11 Dec 2005)
BUNCEFIELD = dict(
    events=[  # (t_h, label, source) -- primary sources only
        (0.0, "Explosion; 20+ tanks involved", "MIIB 2008"),
        (6.0, "Cooling from 1 ML on-site supply (~600,000 L/h); withdrawn after ~2 h", "Atkinson 2017"),
        (11.0, "First foam attack (rim seal) aborted", "Atkinson 2017"),
        (15.0, "Successful foam attack on one tank", "Atkinson 2017"),
        (24.0, "Water supply for main attack took >24 h (1.8-1.9 km relay)", "Atkinson 2017; Wilsher 2025"),
        (26.35, "Main foam attack 08:22 12 Dec", "Wilsher 2025"),
        (73.0, "Fire under control", "MIIB 2006 IR p8"),
        (102.5, "Fire out", "MIIB 2006 IR p8"),
    ],
    foam_used_L=786_000, foam_plan_L=150_000, foam_plan_doubled_L=300_000,
    water_applied_ML=68.0, water_recycled_ML=15.0, retention_ML=2.5, recovered_ML=33.0,
    peak_ff=180, total_ff=1000, n_frs=32, appliance_moves=642,
)

# ---------------------------------------------------------------- Arkema Crosby (hours since 2017-08-28 02:00 CDT, site-wide power loss)
# CSB (2018) Report No. 2017-08-I-TX; paragraph numbers in brackets. Primary source only.
ARKEMA = dict(
    events=[  # (t_h, label, CSB paragraph)
        (-24.0, "Warehouses powered down pre-emptively; products moved to refrigerated trailers; LN2 piping extended", "80, 86-87"),
        (0.0, "Main transformers flooded; site-wide power loss", "12, 91"),
        (3.0, "Last generator shut down; no power to any low-temperature warehouse", "93"),
        (6.0, "LN2 connection submerged (morning); movers fail; 3 trailers stranded in floodwater", "94-95"),
        (34.0, "Ride-out crew evacuated by boat (around midday 29 Aug); 1.5-mile evacuation zone", "105, 110"),
        (72.0, "First trailer decomposes and burns (around 02:00 31 Aug)", "125"),
        (111.0, "Two more trailers burn (around 17:00 1 Sep)", "130"),
        (157.67, "Controlled burn of remaining six trailers (around 15:40 3 Sep)", "140"),
    ],
    n_trailers=9, n_stranded=3, containers_total=10500, containers_stranded=4000, mass_total_lb=350000,
    trailer_endurance_full_tank_d=7.0,   # "more than a week" [55]
    sadt_F=(19.0, 70.0),                 # estimated SADT range of trailer contents [108]
    # Stranded-trailer cooling loss: not timed in the record. Bounded between the morning of 28 Aug,
    # when empty trailers failed as fuel tanks flooded [95], and midday 29 Aug, when the crew left
    # and the stranded trailers' cooling 'likely failed' [106].
    t_cool_loss_h=(6.0, 34.0),
    t_ignition_h=(72.0, 111.0),          # ignition of the three stranded trailers [125, 130]
)
# Planning-parameter ranges for the lumped trailer heat-up (assumed, not from the record).
ARKEMA_PRIOR = dict(
    K_W_m2K=(0.30, 0.70),     # UNECE ATP Annex 1: IR <= 0.40, IN <= 0.70 W m-2 K-1; degraded/flooded up to IN limit
    S_m2=(170.0, 190.0),      # mean body surface of a 53-ft reefer trailer (geometric mean of inside/outside)
    M_t=(15.0, 25.0),         # contents per stranded trailer (~4,000 of 10,500 containers in 3 trailers of 159 t total)
    cp_kJ_kgK=(1.6, 2.4),     # organic peroxide formulations and plastic packaging
    Te_C=(24.0, 32.0),        # outside (air/floodwater) temperature, late-August Gulf Coast
    dT_store_K=(10.0, 25.0),  # storage temperature below SADT at loss of cooling
)
