"""
Module for essential constants in enrich name
"""
import os

import pandas as pd

CURRENT_PATH = os.path.dirname(__file__)

# ? MODEL PATHS
NAME_SPLIT_PATH = f"{CURRENT_PATH}/../data/name_split"

MODEL_PATH = f"{CURRENT_PATH}/../data/transformer_model"

# ? RULE-BASED PATH
RULE_BASED_PATH = f"{CURRENT_PATH}/../data/rule_base/students"

NICKNAME_PATH = f"{CURRENT_PATH}/../data/name_split/nicknames_boundary.parquet"

GENDER_MODEL_PATH = f"{CURRENT_PATH}/../data/gender_model"

GENDER_MODEL_VERSION = "1.0"

PRONOUN_GENDER_RB_PATH = (
    f"{CURRENT_PATH}/../data/gender_model/rule_base/pronoun_gender_dict.parquet"
)

PRONOUN_GENDER_DF = pd.read_parquet(PRONOUN_GENDER_RB_PATH)
PRONOUN_GENDER_MAP = dict(
    zip(PRONOUN_GENDER_DF["pronoun"], PRONOUN_GENDER_DF["gender"])
)

NAME_ELEMENT_PATH = f"{CURRENT_PATH}/../data/name_split/name_elements.parquet"

MF_NAME_GENDER_RULE = pd.read_parquet(
    f"{CURRENT_PATH}/../data/rule_base/gender/mfname.parquet"
)

BEFORE_FNAME_GENDER_RULE = pd.read_parquet(
    f"{CURRENT_PATH}/../data/rule_base/gender/before_fname.parquet"
)

PRONOUN_REGEX = r"^(?:\bkh\b|\bkhach hang\b|\bchị\b|\bchi\b|\banh\b|\ba\b|\bchij\b|\bc\b|\be\b|\bem\b|\bcô\b|\bco\b|\bchú\b|\bbác\b|\bbac\b|\bme\b|\bdì\b|\bông\b|\bong\b|\bbà\b)\s+"
PRONOUN_REGEX_W_DOT = r"^(?:\bkh\b|\bkhach hang\b|\bchị\b|\bchi\b|\banh\b|\ba\b|\bchij\b|\bc\b|\be\b|\bem\b|\bcô\b|\bco\b|\bchú\b|\bbác\b|\bbac\b|\bme\b|\bdì\b|\bông\b|\bong\b|\bbà\b|\ba|\bc)[.,]"

REPLACE_HUMAN_REG_DICT = {"K HI": "", "Bs": "", "Ng.": "Nguyễn"}

BRIEF_NAME_DICT = {"nguyen": ["ng.", "n."], "do": ["d."], "pham": ["p."]}

# * NICKNAMES
NICKNAMES = pd.read_parquet(NICKNAME_PATH)
NICKNAME_REGEX = "|".join(
    [
        *NICKNAMES["name"].to_list(),
        *NICKNAMES[NICKNAMES["de_name"].str.split().str.len() > 1]["de_name"].to_list(),
    ]
)

# * NAME POSSIBLE ELEMENTS
NAME_ELEMENTS = pd.read_parquet(NAME_ELEMENT_PATH)
WITHOUT_ACCENT_ELEMENTS = set(NAME_ELEMENTS["without_accent"].unique())
WITH_ACCENT_ELEMENTS = set(NAME_ELEMENTS["with_accent"].unique())

# * NAME ELEMENTS POPULARITY
WITHOUT_ACCENT_ELEMENT_POPULARITY = (
    pd.read_parquet(
        f"{CURRENT_PATH}/../data/name_split/popular_name_without_accent_elements.parquet"
    )
    .set_index("without_accent")
    .to_dict()["count"]
)
WITH_ACCENT_ELEMENT_POPULARITY = (
    pd.read_parquet(
        f"{CURRENT_PATH}/../data/name_split/popular_name_with_accent_elements.parquet"
    )
    .set_index("with_accent")
    .to_dict()["count"]
)

# * LASTNAME IS FIRSTNAME
LASTNAME_IS_FIRSTNAME = pd.read_parquet(
    f"{CURRENT_PATH}/../data/name_split/lastname_is_firstname.parquet"
)["with_accent"].to_list()
