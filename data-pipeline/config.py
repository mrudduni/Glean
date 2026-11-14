"""Shared configuration for the Team Brackets data pipeline.

Everything that more than one script needs lives here: paths, the study area,
year ranges, the CDL -> CropId map, and environment variables.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------- paths
ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
OUT = ROOT / "out"
PROCESSED = OUT / "processed"
WEB = OUT / "web"
WEB_FIELD = WEB / "field"
REPO = ROOT.parent
DOCS = REPO / "docs"

load_dotenv(ROOT / ".env")

EARTHDATA_USERNAME = os.getenv("EARTHDATA_USERNAME", "").strip()
EARTHDATA_PASSWORD = os.getenv("EARTHDATA_PASSWORD", "").strip()
NASS_API_KEY = os.getenv("NASS_API_KEY", "").strip()
OPENET_API_KEY = os.getenv("OPENET_API_KEY", "").strip()


def has_earthdata() -> bool:
    """True if Earthdata creds are in .env or ~/.netrc / ~/_netrc."""
    if EARTHDATA_USERNAME and EARTHDATA_PASSWORD:
        return True
    for name in (".netrc", "_netrc"):
        p = Path.home() / name
        if p.exists() and "urs.earthdata.nasa.gov" in p.read_text(errors="ignore"):
            return True
    return False


# ---------------------------------------------------------------- study area
STATE_FIPS = "20"
COUNTY_FIPS = "055"
COUNTY_FIPS_FULL = "20055"
COUNTY_NAME = "FINNEY"
STATE_ALPHA = "KS"
NASS_DISTRICT = "SOUTHWEST"

# Rough bounding box of Finney County (lon_min, lat_min, lon_max, lat_max).
# Only used for quick pre-filters; exact clipping uses the TIGER outline.
COUNTY_BBOX = (-101.11, 37.64, -100.21, 38.27)

FIELD_IDS = ["f1", "f2", "f3"]

FIELD_META = {
    "f1": {
        "kind": "irrigated_pivot",
        "name": {"en": "North pivot (irrigated)", "es": "Pivote norte (riego)"},
    },
    "f2": {
        "kind": "dryland",
        "name": {"en": "Dryland wheat field", "es": "Campo de trigo de secano"},
    },
    "f3": {
        "kind": "sandy_wind",
        "name": {"en": "Sandy field", "es": "Campo arenoso"},
    },
}

# ---------------------------------------------------------------- years
CSB_RELEASE = "NationalCSB_2018-2025_rev23"
CSB_URL = (
    "https://www.nass.usda.gov/sites/default/files/Research_and_Science/"
    f"Crop-Sequence-Boundaries/datasets/{CSB_RELEASE}.zip"
)
CROP_YEARS = list(range(2018, 2026))  # 8 seasons, oldest -> newest

POWER_START, POWER_END = "19810101", "20251231"
PRISM_START, PRISM_END = "19910101", "20251231"
MODIS_START, MODIS_END = "2000-01-01", "2025-12-31"
SMAP_START, SMAP_END = "2015-04-01", "2025-12-31"
ECOSTRESS_START, ECOSTRESS_END = "2018-07-01", "2025-12-31"
IMERG_START = "2000-06-01"
OPENET_START = "2016-01-01"
GRACE_GAP = ("2017-07", "2018-05")  # inclusive, between missions

NDVI_NORMAL_YEARS = [2016, 2017, 2018, 2019]
DROUGHT_YEARS = [2002, 2011, 2012, 2018, 2020, 2022]

# ---------------------------------------------------------------- CDL map
# CDL code -> CropId. Anything not listed maps to "other".
CDL_TO_CROP = {
    1: "corn",
    2: "cotton",
    4: "sorghum",
    5: "soybean",
    24: "wheat",
    26: "wheat",     # Dbl Crop WinWht/Soybeans
    236: "wheat",    # Dbl Crop WinWht/Sorghum
    27: "rye_cover",
    36: "alfalfa",
    61: "fallow",
    205: "triticale",
}
DOUBLE_CROP_CODES = {26, 236}

# Names from the CDL legend for the codes we expect in Finney County.
CDL_NAMES = {
    0: "Background", 1: "Corn", 2: "Cotton", 3: "Rice", 4: "Sorghum", 5: "Soybeans",
    6: "Sunflower", 12: "Sweet Corn", 21: "Barley", 22: "Durum Wheat", 23: "Spring Wheat",
    24: "Winter Wheat", 25: "Other Small Grains", 26: "Dbl Crop WinWht/Soybeans",
    27: "Rye", 28: "Oats", 29: "Millet", 31: "Canola", 33: "Safflower", 36: "Alfalfa",
    37: "Other Hay/Non Alfalfa", 42: "Dry Beans", 43: "Potatoes", 44: "Other Crops",
    53: "Peas", 58: "Clover/Wildflowers", 59: "Sod/Grass Seed", 61: "Fallow/Idle Cropland",
    111: "Open Water", 121: "Developed/Open Space", 122: "Developed/Low Intensity",
    123: "Developed/Med Intensity", 124: "Developed/High Intensity", 131: "Barren",
    141: "Deciduous Forest", 152: "Shrubland", 176: "Grassland/Pasture",
    190: "Woody Wetlands", 195: "Herbaceous Wetlands", 205: "Triticale",
    225: "Dbl Crop WinWht/Corn", 226: "Dbl Crop Oats/Corn", 228: "Dbl Crop Triticale/Corn",
    236: "Dbl Crop WinWht/Sorghum", 237: "Dbl Crop Barley/Corn", 238: "Dbl Crop WinWht/Cotton",
    240: "Dbl Crop Soybeans/Oats", 241: "Dbl Crop Corn/Soybeans",
}


def cdl_to_crop(code) -> str:
    try:
        return CDL_TO_CROP.get(int(code), "other")
    except (TypeError, ValueError):
        return "other"


def cdl_name(code) -> str:
    try:
        return CDL_NAMES.get(int(code), f"CDL {int(code)}")
    except (TypeError, ValueError):
        return "Unknown"


# ---------------------------------------------------------------- rotation map (README §7.2)
CLASS_TO_ROTATION = {
    "corn_wheat_sorghum": "R1",
    "wsf": "R2",
    "alfalfa": "R4",
    "corn_soy": "R5",
}

# ---------------------------------------------------------------- CRS
CRS_WGS84 = "EPSG:4326"
CRS_UTM14 = "EPSG:32614"   # metric work in Finney County
HA_TO_AC = 2.471

# ---------------------------------------------------------------- neighbours
NEIGHBOR_RADIUS_KM = 25
NEIGHBOR_MIN_HA, NEIGHBOR_MAX_HA = 20, 130
NEIGHBOR_MIN_KNOWN_YEARS = 6
NEIGHBOR_POOL_MAX = 150
NEIGHBOR_K = 30
IRRIGATED_NDVI_PEAK = 0.75

USER_AGENT = "TeamBrackets-SpaceApps2026-data-pipeline/1.0"
