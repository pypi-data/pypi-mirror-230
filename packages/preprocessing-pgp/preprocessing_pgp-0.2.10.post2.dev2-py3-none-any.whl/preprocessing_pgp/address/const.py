"""
File containing constants that are necessary for processing address extraction
"""

import os

import pandas as pd

CURRENT_PATH = os.path.dirname(__file__)

# ? REGEX FOR ADDRESS
DICT_NORM_ABBREV_REGEX_KW = {
    "Tp ": ["Tp.", "Tp:"],
    "Tt ": ["Tt.", "Tt:"],
    "Q ": ["Q.", "Q:"],
    "H ": ["H.", "H:"],
    "X ": ["X.", "X:"],
    "P ": ["P.", "P:"],
}

DICT_NORM_CITY_DASH_REGEX = {
    " Bà Rịa - Vũng Tàu ": [
        "Ba Ria Vung Tau",
        "Bà Rịa-Vũng Tàu",
        "Ba Ria-Vung Tau",
        "Brvt",
        "Br-Vt",
    ],
    " Phan Rang-Tháp Chàm ": [
        "Phan Rang Thap Cham",
        "Phan Rang - Tháp Chàm",
        "Phan Rang - Thap Cham",
        "Prtc",
        "Pr-Tc",
    ],
    " Thua Thien Hue ": ["Thua Thien - Hue", "Hue"],
    " Hồ Chí Minh ": ["Sài Gòn", "Sai Gon"],
    " Đà Nẵng ": [
        "Quang Nam-Da Nang",
        "Quảng Nam-Đà Nẵng",
        "Quang Nam - Da Nang",
        "Quảng Nam - Đà Nẵng",
        "Qndn",
        "Qn-Dn",
    ],
    " Đắk Lắk ": [
        "Dac Lac",
        "Đắc Lắc",
        "Daclac",
    ],
    " Đắk Nông ": [
        "Dac Nong",
        "Đắc Nông",
        "Dacnong",
    ],
    " Kon Tum ": [
        "Con Tum",
        "Contum",
    ],
    " Bắc Kạn ": [
        "Bắc Cạn",
        "Bac Can",
    ]
    # " Thành Phố ": ["Tp"],
}

ADDRESS_PUNCTUATIONS = ["-", "/", "'"]

ADDRESS_ADDITIONAL_NON_BOUNDARY = ["'", "/"]

NON_STREET_PATTERNS = [
    "x",
    "tp",
    "tt",
    "h",
    "q",
    "tx",
    "p",
    "t",
    "xã",
    "tỉnh",
    "huyện",
    "việt nam",
    "vietnam",
    "viet nam",
]

# ? LEVEL METHODS
LV1_METHODS = [
    "lv1_title",
    "lv1_title_abbrev",
    "lv1_norm",
    "lv1_abbrev",
    "lv1_glue_norm",
    "lv1_glue_abbrev",
    "lv1_prefix_im",
    "lv1_nprefix_im",
    "lv1_code_name",
]
LV2_METHODS = [
    "lv2_title",
    "lv2_title_abbrev",
    "lv2_norm",
    "lv2_abbrev",
    "lv2_glue_norm",
    "lv2_glue_abbrev",
    "lv2_prefix_im",
    # "lv2_nprefix_im",
]
LV3_METHODS = [
    "lv3_title",
    "lv3_title_abbrev",
    "lv3_norm",
    "lv3_abbrev",
    "lv3_glue_norm",
    "lv3_glue_abbrev",
    "lv3_prefix_im",
    # "lv3_nprefix_im",
]
ADVANCED_METHODS = ["home_credit_key"]
METHOD_REFER_DICT = {1: LV1_METHODS, 2: LV2_METHODS, 3: LV3_METHODS}

# ? LOCATION ENRICH DICTIONARY
__LOCATION_ENRICH_PATH = f"{CURRENT_PATH}/../data/location_dict_enrich_address.parquet"
LOCATION_ENRICH_DICT = pd.read_parquet(__LOCATION_ENRICH_PATH)

# ? LOCATION CODE DICTIONARY
__LOCATION_CODE_PATH = f"{CURRENT_PATH}/../data/location_dict_code_new.parquet"
LOCATION_CODE_DICT = pd.read_parquet(__LOCATION_CODE_PATH)

LEVEL_VI_COLUMN_DICT = {1: "city_vi", 2: "district_vi", 3: "ward_vi"}
LEVEL_CODE_COLUMN_DICT = {1: "city_code", 2: "district_code", 3: "ward_code"}
LEVEL_ID_COLUMN_DICT = {1: "city_id", 2: "district_id", 3: "ward_id"}

AVAIL_LEVELS = LEVEL_VI_COLUMN_DICT.keys()
