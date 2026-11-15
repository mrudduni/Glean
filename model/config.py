"""Every path and tunable constant the model uses. docs/METHODS.md lists each one with its source."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

MODEL_DIR = Path(__file__).resolve().parent
REPO_DIR = MODEL_DIR.parent

load_dotenv(MODEL_DIR / ".env")
load_dotenv(Path.home() / ".glean" / ".env")
load_dotenv(Path.home() / ".fieldshift" / ".env")


def _path(env: str, default: Path | str) -> Path:
    raw = os.environ.get(env)
    path = Path(raw) if raw else Path(default)
    return path if path.is_absolute() else (MODEL_DIR / path).resolve()


# ---------------------------------------------------------------- paths
# D's pipeline output (contains processed/ and web/). Point at model/mock_inputs to run without D.
DATA_DIR = _path("DATA_DIR", "C:/Users/HP/fieldshift-data/data-pipeline/out")
CONTENT_DIR = _path("CONTENT_DIR", "../content")
OUT_DIR = _path("MODEL_OUT_DIR", MODEL_DIR / "out" / "web")
DEFAULT_CROPS_YAML = MODEL_DIR / "library" / "default_crops.yaml"
CONTENT_GIT_REF = "origin/role/content"  # fallback source for content/crops.yaml

# ---------------------------------------------------------------- ids (README 7.2)
FIELD_IDS = ["f1", "f2", "f3"]
CROP_IDS = ["corn", "sorghum", "wheat", "soybean", "alfalfa", "triticale", "rye_cover", "cotton", "fallow"]
ROTATION_IDS = ["R0", "R1", "R2", "R3", "R4", "R5", "R6"]
CAP_IDS = ["dryland", "cap150", "cap300", "cap450"]
CLIMATE_IDS = ["actual", "hotdry"]
SCENARIOS = [f"{c}|{k}" for c in CAP_IDS for k in CLIMATE_IDS]
DEFAULT_SCENARIO = "cap300|actual"
CRITERIA = ["water_use", "income_mean", "income_worst", "soil_health",
            "water_erosion", "wind_erosion", "pest_break", "heat_frost_risk"]
SOURCE_TAGS = ["POWER", "IMERG", "SMAP", "MODIS", "HLS", "ECOSTRESS", "GRACE", "SRTM", "SSURGO", "CSB",
               "NASS", "OpenET", "PRISM", "USGS", "CoCoRaHS", "GAEZ", "AMS", "FAO56", "MODEL"]

# ---------------------------------------------------------------- replay period
YEAR_FROM, YEAR_TO = 2000, 2025
SPINUP_START = "1999-10-01"
SPINUP_DEPLETION_FRAC = 0.5          # start at 50 % depletion of the profile
N_YEARS = YEAR_TO - YEAR_FROM + 1     # 26, used in heat_frost_risk

# ---------------------------------------------------------------- scenarios
CAP_MM = {"dryland": 0.0, "cap150": 150.0, "cap300": 300.0, "cap450": 450.0}  # per crop season
HOTDRY_DT_C = 1.5                     # added to tmax, tmin, tmean
HOTDRY_P_FACTOR = 0.85                # precipitation multiplier

# ---------------------------------------------------------------- soil water bucket (FAO-56 ch. 8)
ZMAX_M = 1.5                          # profile depth cap
ROOT_INIT_M = 0.15                    # root depth at planting
PIVOT_EFFICIENCY = 0.85               # fraction of applied water that reaches the root zone
# When a full refill would pass the season cap, apply what is left of the cap (if at least this much).
# The handover rule skipped the refill entirely, which let capped irrigation fall under hotdry.
IRR_MIN_EVENT_MM = 5.0
STRESS_KS = 0.8                       # stress day if Ks below this
BARE_KE = 0.30                        # bare soil evaporation coefficient (x ET0)
BARE_STAGE1_MM = 12.0                 # readily evaporable water before evaporation slows
BARE_DECAY_FRAC = 0.4                 # f decays over 0.4 x TAW_profile beyond stage 1
BARE_F_MIN = 0.1
# On bare days evaporation draws from a surface layer of this depth (FAO-56 ch. 7, Ze 0.10-0.15 m,
# https://www.fao.org/4/x0490e/x0490e0c.htm); water below it is stored for the next crop.
BARE_EVAP_DEPTH_M = 0.15
# SCS curve number, row crop, straight row, good condition (NRCS NEH 630 ch. 9, table 9-1, https://directives.nrcs.usda.gov/sites/default/files2/1720460895/Chapter%209%20-%20Hydrologic%20Soil-Cover%20Complexes.pdf)
CN_BY_HYDGRP = {"A": 67, "B": 78, "C": 85, "D": 89}
CN_BARE_ADD = 3
CN_IA_RATIO = 0.2                     # initial abstraction = 0.2 S

# ---------------------------------------------------------------- crop timing
MIN_GAP_DAYS = 5                      # days between one harvest and the next planting
FALLOW_END_MMDD = "07-01"             # a fallow step lasts until this date of the following year
ALFALFA_DORMANT_KC = 0.40             # Kc of an established alfalfa stand between seasons
# R3 "flex fallow" grows spring triticale for forage in the fallow window of wheat-sorghum-fallow
# (Holman et al. 2022, Crop Science 62:1-17, https://doi.org/10.1002/csc2.20670). crops.yaml lists a
# fall-planted triticale, which cannot follow an October sorghum harvest, so the replay uses this
# spring timing. Kc, p, Ky and roots stay as crops.yaml (winter wheat proxy).
TRITICALE_SPRING = {
    "plant_window": {"start": "03-10", "end": "04-05"},
    "harvest_window": {"start": "05-25", "end": "06-15"},
    "stage_days": {"ini": 15, "dev": 30, "mid": 20, "late": 12},
}

# ---------------------------------------------------------------- yield and revenue
HEAT_LOSS_PER_DAY = 0.015
# Heat days are counted only in the first 21 days of the crop's sensitive stage (corn pollination and
# silking last about 2-3 weeks; K-State Corn Production Handbook C560,
# https://bookstore.ksre.ksu.edu/pubs/C560.pdf). Counting the whole FAO mid stage (about 47 days for
# corn) cut irrigated corn to about 58 % of the NASS mean yield, which double-counts heat already in
# that mean.
HEAT_WINDOW_DAYS = 21
HEAT_FACTOR_MIN = 0.5
FROST_FACTOR = 0.85
# spring freeze for winter crops: winter-hardy (frost_kill_c) while dormant, but 28 F for 2 h kills florets at boot/heading
# https://bookstore.ksre.ksu.edu/pubs/spring-freeze-injury-to-kansas-wheat_C646.pdf
SPRING_FREEZE_SEASONS = ("winter", "cover")
SPRING_FREEZE_START = "03-15"     # green-up
SPRING_FREEZE_C = -2.2
SPRING_FREEZE_MONTHS = {3, 4, 5}  # calendar frost flag months for winter crops
NASS_RECENT_FROM, NASS_RECENT_TO = 2010, 2024   # prefer yields from this window
NASS_N_YEARS = 5                                # mean of the most recent 5 values
NASS_MIN_VALUES = 3
PRICE_YEARS = (2020, 2024)                      # 5-year mean price
NASS_LEVEL_ORDER = ["county", "district", "state"]

# ---------------------------------------------------------------- exposure and erosion
RESIDUE_FACTOR = {"high": 0.5, "medium": 0.7, "low": 0.9}
RESIDUE_DAYS = 120
STORM_MM = 12.7                       # 0.5 in
WINDY_MS = 11.0                       # ws10m_max, about 25 mph
WEI_MAX = 310.0                       # WEG 1 maximum wind erodibility index, t/ac/yr

# ---------------------------------------------------------------- drought years
DROUGHT_P_QUANTILE = 0.20             # Jun-Aug precip in lowest 20 %
DROUGHT_ET0_QUANTILE = 0.70           # Jun-Aug ET0 in highest 30 %
DROUGHT_NDVI_ANOM_PCT = -10.0

# ---------------------------------------------------------------- calendar
CAL_HEAT_TMAX = 35.0
CAL_HEAT_MIN_DAYS = 3
CAL_FROST_TMIN = -2.0
CAL_DRY_RUN_DAYS = 21
CAL_DRY_MM = 2.0
CAL_FLAG_P = 0.3
CAL_STORM_DAYS = 1.0
CAL_WINDY_DAYS = 2.0

# ---------------------------------------------------------------- scoring
SOIL_W = {"living_root": 40, "residue": 20, "legume": 15, "families": 15, "not_bare": 10}
RESIDUE_SCORE = {"high": 1.0, "medium": 0.6, "low": 0.2, "none": 0.0}
FAMILIES_FULL = 4
PEST_RUN_CAP = 8
FROST_WEIGHT = 2.0
BENEFIT_WATER_MM = 25
BENEFIT_BARE_DAYS = 20
BENEFIT_WORST5_USD = 10
NEIGHBOR_MIN_N = 3
# default slider weights (web handover 4.x: 3 each) and README 8.7 mapping, used only for acceptance checks
SLIDER_DEFAULT = {"save_water": 3, "income": 3, "steady_income": 3, "soil_health": 3, "erosion": 3}
SLIDER_SHARES = {
    "save_water": {"water_use": 1.0},
    "income": {"income_mean": 1.0},
    "steady_income": {"income_worst": 0.7, "heat_frost_risk": 0.3},
    "soil_health": {"soil_health": 0.7, "pest_break": 0.3},
    "erosion": {"wind_erosion": 0.6, "water_erosion": 0.4},
}

# ---------------------------------------------------------------- climate summary
NORMAL_PERIOD = (1991, 2020)
RECENT_PERIOD = (2016, 2025)
FROST_C = 0.0
GDD_BASE_C, GDD_CAP_C = 10.0, 30.0
HOT_DAY_C = 35.0
OUTLOOK_GRACE_CM = 0.3
OUTLOOK_WELL_M = 0.1

# ---------------------------------------------------------------- validation
VALID_YEARS = (2016, 2025)            # clipped to the crop-history years D provides
VALID_MONTHS = range(4, 11)           # Apr-Oct
ACTUAL_RUN_CAP = "cap450"             # irrigated fields run with full irrigation for the actual-history check
SMAP_YEARS = (2015, 2025)
LEVELS = {
    "et_vs_openet": {"good": (15, 0.6), "fair": (30, None)},          # |bias| %, r2
    "precip": {"good": (10, 0.8), "fair": (20, None)},               # |bias| %, r
    "sm_vs_smap": {"good": 0.6, "fair": 0.4},                        # r
}
