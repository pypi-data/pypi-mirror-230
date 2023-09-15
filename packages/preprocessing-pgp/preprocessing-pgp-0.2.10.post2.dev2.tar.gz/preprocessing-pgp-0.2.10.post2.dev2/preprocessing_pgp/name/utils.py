"""
Module contains tools for processing name
"""

import pandas as pd
from preprocessing_pgp.name.const import (
    NICKNAME_REGEX,
    WITH_ACCENT_ELEMENT_POPULARITY,
    WITHOUT_ACCENT_ELEMENT_POPULARITY,
)
from unidecode import unidecode


def remove_nicknames(name_df: pd.DataFrame, name_col: str) -> pd.DataFrame:
    """
    Remove nicknames in name column given the data

    Parameters
    ----------
    name_df : pd.DataFrame
        The data process
    name_col : str
        The name column in data to remove nickname

    Returns
    -------
    pd.DataFrame
        Cleaned data without nickname -- added new column `clean_name_col`
    """
    name_df[name_col] = (
        name_df[name_col].str.replace(NICKNAME_REGEX, "", regex=True).str.strip()
    )

    return name_df


def is_name_accented(name: str) -> bool:
    """
    Check whether the name is accented or not

    Parameters
    ----------
    name : str
        The input name

    Returns
    -------
    bool
        Whether the name is accented
    """
    return unidecode(name) != name


def get_name_popularity(name: str, popularity_dict: dict) -> int:
    """
    Get the name popularity from dict

    Parameters
    ----------
    name : str
        The input name to get popularity
    popularity_dict : pd.DataFrame
        Popularity dictionary from hdfs

    Returns
    -------
    int
        The popularity if exist, otherwise 0
    """
    return popularity_dict.get(name.lower(), 0)


def choose_best_name(raw_name: str, enrich_name: str) -> str:
    """
    Choose the best name element from raw and inference to get the best of all the possibilities

    Parameters
    ----------
    raw_name : str
        The raw input name (better if cleaned)
    enrich_name : str
        The inference name from the raw name

    Returns
    -------
    str
        The best possible name that we can get
    """

    # * Edge case -- All names are None
    if all([None in [raw_name, enrich_name]]):
        return None

    # * Split name into elements to process better
    raw_components = raw_name.split(" ")
    enrich_components = enrich_name.split(" ")

    # * Wrong enrich - the number of components are different
    if len(raw_components) != len(enrich_components):
        return raw_name

    # * Loop through all components -> Find best name components
    best_name_components = []
    for raw_component, enrich_component in zip(raw_components, enrich_components):
        # ? Get with_accent popularity
        raw_popularity = get_name_popularity(
            raw_component, WITH_ACCENT_ELEMENT_POPULARITY
        )
        enrich_popularity = get_name_popularity(
            enrich_component, WITH_ACCENT_ELEMENT_POPULARITY
        )

        # ? CASE 1: MAX popularity is not 0
        max_popularity = max(raw_popularity, enrich_popularity)
        if max_popularity != 0:
            best_component = (
                enrich_component
                if enrich_popularity == max_popularity
                else raw_component
            )
            best_name_components.append(best_component)
            continue

        # ? CASE 2: Both not have the popularity (not exist in dictionary)
        de_raw_popularity = get_name_popularity(
            raw_component, WITHOUT_ACCENT_ELEMENT_POPULARITY
        )
        de_enrich_popularity = get_name_popularity(
            enrich_component, WITHOUT_ACCENT_ELEMENT_POPULARITY
        )

        max_de_popularity = max(de_raw_popularity, de_enrich_popularity)
        # ? SUB CASE 2: MAX de_popularity is 0 =>> Skip
        if max_de_popularity == 0:
            continue

        # ? Else choose the most popular one
        best_de_component = (
            enrich_component
            if de_enrich_popularity == max_de_popularity
            else raw_component
        )
        best_name_components.append(best_de_component)

    return " ".join(best_name_components).strip().title()
