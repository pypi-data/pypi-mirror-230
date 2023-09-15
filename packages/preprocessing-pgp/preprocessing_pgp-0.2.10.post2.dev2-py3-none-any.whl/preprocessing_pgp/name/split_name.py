"""
Module support extra function to process name
"""

import re
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from flashtext import KeywordProcessor
from preprocessing_pgp.name.const import (
    BRIEF_NAME_DICT,
    LASTNAME_IS_FIRSTNAME,
    NAME_SPLIT_PATH,
)
from preprocessing_pgp.name.utils import get_name_popularity
from tqdm import tqdm
from unidecode import unidecode

tqdm.pandas()


def build_last_name(base_path: str):
    # load stats lastname
    stats_lastname_vn = pd.read_parquet(f"{base_path}/stats_lastname_vn.parquet")

    lastname_list = list(
        stats_lastname_vn.sort_values(by="n_citizen", ascending=False)[
            "with_accent"
        ].unique()
    )

    popularity_dict = stats_lastname_vn.set_index("with_accent").to_dict()["n_citizen"]

    # return
    return lastname_list, popularity_dict


def build_word_name(base_path: str):
    threshold = 5  # at least 5 appearance
    stats_word_name = pd.read_parquet(
        f"{base_path}/popular_name_with_accent_elements.parquet"
    ).query(f"count >= {threshold}")
    stats_de_word_name = pd.read_parquet(
        f"{base_path}/popular_name_without_accent_elements.parquet"
    ).query(f"count >= {threshold}")

    word_name = set(
        set(stats_word_name["with_accent"].unique())
        | set(stats_de_word_name["without_accent"].unique())
    )
    return word_name


class NameProcess:
    def __init__(self):
        self.word_name = np.array(list(build_word_name(NAME_SPLIT_PATH)))
        self.last_name_list, self.last_name_popularity = build_last_name(
            NAME_SPLIT_PATH
        )
        self.last_name_regex = "|".join(self.last_name_list)
        self.__generate_brief_keywords()
        self.brief_name_terms = list(self.brief_name_kws.get_all_keywords().keys())

    def __generate_brief_keywords(self):
        if hasattr(self, "brief_name_kws"):
            return

        kws = KeywordProcessor(case_sensitive=True)
        kws.add_keywords_from_dict(BRIEF_NAME_DICT)

        self.brief_name_kws = kws

    def CountNameVN(self, text):
        try:
            text = unidecode(text.lower())

            # Contains 1 char
            if len(text) == 1:
                return 1

            # Check in word_name
            word_text = np.array(text.split())

            # Handle case where 2 word with same decode in name
            intersect_bool = np.in1d(word_text, self.word_name)
            intersect_score = np.sum(intersect_bool)

            # name containing brief 1 word and brief name
            brief_score = np.sum(np.in1d(word_text, self.brief_name_terms))

            return intersect_score + brief_score

        except:
            return -1

    def check_name_valid(self, series: pd.Series) -> pd.Series:
        de_data = series.apply(unidecode).str.lower().str.split(expand=True)

        name_valid = de_data.apply(lambda row: row.isin(self.word_name).all())

        return name_valid

    def _get_name_popularity_dict(
        self, names: List[str], refer_dict: Dict[str, int]
    ) -> Dict[str, int]:
        popularity_dict = dict(
            sorted(
                zip(names, [get_name_popularity(name, refer_dict) for name in names]),
                key=lambda item: item[1],
                reverse=True,
            )
        )

        return popularity_dict

    def _two_word_split(self, full_name: str) -> Tuple[str, str, str]:
        """
        Process split name case 2 words

        Parameters
        ----------
        full_name : str
            The name with only 2 words

        Returns
        -------
        Tuple[str, str, str]
            Name parts in order last, middle, first
        """
        name_parts = full_name.split(" ")

        # * Case 1: Both part is last-name
        if all(part in self.last_name_list for part in name_parts):
            ln_is_fn_dict = dict(
                zip(name_parts, [part in LASTNAME_IS_FIRSTNAME for part in name_parts])
            )
            # ? 1 last name is first name
            if sum(ln_is_fn_dict.values()) == 1:
                if ln_is_fn_dict[name_parts[0]]:
                    return name_parts[1], None, name_parts[0]  # fn - ln

                return name_parts[0], None, name_parts[1]  # ln - fn
            # ? other cases: no ln is fn or 2 ln is fn
            return name_parts[0], None, name_parts[1]  # ln - fn

        # * Case 2: one part is last-name
        if name_parts[0] in self.last_name_list:
            return name_parts[0], None, name_parts[1]  # ln - fn
        if name_parts[1] in self.last_name_list:
            return name_parts[1], None, name_parts[0]  # fn - ln

        # * Case 3: no last name
        return None, name_parts[0], name_parts[1]  # mn - fn

    def _multi_word_split(self, full_name: str) -> Tuple[str, str, str]:
        """
        Process split name case multiple words (> 2)

        Parameters
        ----------
        full_name : str
            The name with more than 2 words

        Returns
        -------
        Tuple[str, str, str]
            Name parts in order last, middle, first
        """

        name_parts = full_name.split(" ")

        first_parts = name_parts[:-2]
        last_parts = name_parts[-2:]
        # * Case 1: Two last part is last name
        if all(part in self.last_name_list for part in last_parts):
            # ? Check last part in firstname alike
            if last_parts[1] in LASTNAME_IS_FIRSTNAME:
                last_parts = last_parts[::-1]

            # ? Move both last name into [0, 1]
            name_parts = [*last_parts, *first_parts]
            return name_parts[0], " ".join(name_parts[1:-1]), name_parts[-1]

        # * Case 2: Two last part contains 1 last name
        if any(part in self.last_name_list for part in last_parts):
            if last_parts[1] in self.last_name_list:
                # ? last is last name
                name_parts = [name_parts[-1], *name_parts[:-1]]
            else:
                # ? last is not last name
                if name_parts[-3] in self.last_name_list:
                    name_parts = [*name_parts[-3:], *name_parts[:-3]]
                else:
                    name_parts = [*last_parts, *first_parts]
            return name_parts[0], " ".join(name_parts[1:-1]), name_parts[-1]

        # * Case 3: fist parts is more than a word
        if len(first_parts) > 1:
            if first_parts[0] not in self.last_name_list:
                # ? second word is last name
                if first_parts[1] in self.last_name_list:
                    name_parts = [first_parts[1], *name_parts[2:], first_parts[0]]

        return name_parts[0], " ".join(name_parts[1:-1]), name_parts[-1]

    def split_name(self, full_name: str) -> Tuple[str, str, str]:
        """
        Split name into three parts:
        * First name
        * Middle name
        * Last name

        Parameters
        ----------
        full_name : str
            The input full name

        Returns
        -------
        Tuple[str, str, str]
            The tuple of the following order: last, middle, first
        """
        first_name: str = None
        middle_name: str = None
        last_name: str = None
        # ? Input name not exist
        if full_name is None or full_name == "" or not isinstance(full_name, str):
            return None, None, None

        # ? Pre-process full name
        full_name = re.sub(r"\s+", " ", full_name).strip().lower()
        name_parts = full_name.split(" ")

        # * EDGE CASE: Full name contains only 1 word ---> First name
        if len(name_parts) == 1:
            return None, None, full_name

        # * CASE 1: Name only 2 words
        if len(name_parts) == 2:
            # print("two words")
            last_name, middle_name, first_name = self._two_word_split(full_name)

        # * CASE 2: Name contains more than 2 words
        if len(name_parts) > 2:
            # print("multi words")
            last_name, middle_name, first_name = self._multi_word_split(full_name)

        # ? Format element
        first_name = first_name.title() if first_name is not None else None
        middle_name = middle_name.title() if middle_name is not None else None
        last_name = last_name.title() if last_name is not None else None

        return last_name, middle_name, first_name

    # Split name into parts
    def SplitName(self, full_name: str):
        try:
            # Variable
            use_only_last_name = True
            full_name = full_name.replace(r"\s+", " ").strip().lower()
            last_name = ""
            middle_name = None
            first_name = None

            # Case 0: full name only have 1 word
            if len(full_name.split(" ")) == 1:
                # print('Case 0')
                first_name = full_name
                return last_name, middle_name, first_name

            # Case 1: Nguyen Van C ---> last-middle-first
            check_end_case1 = False
            while not check_end_case1:
                for key_vi in self.last_name_list:
                    key_vi = key_vi + " "

                    is_case11 = full_name.find(key_vi) == 0
                    is_case12 = full_name.find(unidecode(key_vi)) == 0
                    is_case1 = is_case11 or is_case12
                    if is_case1:
                        # print('Case 1')
                        key = key_vi if is_case11 else unidecode(key_vi)

                        last_name = (last_name + " " + key).strip()
                        full_name = full_name.replace(key, "", 1).strip()

                        if use_only_last_name:
                            check_end_case1 = True
                        break

                    if (full_name.split(" ") == 1) or (
                        key_vi.strip() == self.last_name_list[-1]
                    ):
                        check_end_case1 = True

            # Case 2: Van D Nguyen
            if last_name.strip() == "":
                check_end_case2 = False
                while not check_end_case2:
                    for key_vi in self.last_name_list:
                        key_vi = " " + key_vi

                        is_case21 = (
                            len(full_name) - full_name.rfind(key_vi) == len(key_vi)
                        ) & (full_name.rfind(key_vi) != -1)
                        is_case22 = (
                            len(full_name) - full_name.rfind(unidecode(key_vi))
                            == len(unidecode(key_vi))
                        ) & (full_name.rfind(unidecode(key_vi)) != -1)

                        is_case2 = is_case21 or is_case22
                        if is_case2:
                            # print('Case 2')
                            key = key_vi if is_case21 else unidecode(key_vi)

                            last_name = (key + " " + last_name).strip()
                            full_name = "".join(full_name.rsplit(key, 1)).strip()

                            if use_only_last_name:
                                check_end_case2 = True
                            break

                        if (full_name.split(" ") == 1) or (
                            key_vi.strip() == self.last_name_list[-1]
                        ):
                            check_end_case2 = True

            # Case 3: E Nguyen Van
            if last_name.strip() == "":
                temp_full_name = full_name
                temp_first_name = temp_full_name.split(" ")[0]
                temp_full_name = " ".join(temp_full_name.split(" ")[1:]).strip()

                check_end_case3 = False
                while not check_end_case3:
                    for key_vi in self.last_name_list:
                        key_vi = key_vi + " "

                        is_case31 = temp_full_name.find(key_vi) == 0
                        is_case32 = temp_full_name.find(unidecode(key_vi)) == 0
                        is_case3 = is_case31 or is_case32
                        if is_case3:
                            # print('Case 3')
                            key = key_vi if is_case31 else unidecode(key_vi)

                            last_name = (last_name + " " + key).strip()
                            temp_full_name = temp_full_name.replace(key, "", 1).strip()

                            if use_only_last_name:
                                check_end_case3 = True
                            break

                        if (full_name.split(" ") == 1) or (
                            key_vi.strip() == self.last_name_list[-1]
                        ):
                            check_end_case3 = True

                if last_name.strip() != "":
                    first_name = temp_first_name
                    middle_name = temp_full_name

                    return (
                        last_name.title(),
                        middle_name.title(),
                        first_name.title(),
                    )

            # Fillna
            first_name = full_name.split(" ")[-1]
            try:
                full_name = "".join(full_name.rsplit(first_name, 1)).strip()
                middle_name = full_name
            except:
                # print('Case no middle name')
                middle_name = None

            # Replace '' to None
            last_name = None if (last_name == "") else last_name.title()
            middle_name = None if (middle_name == "") else middle_name.title()
            first_name = None if (first_name == "") else first_name.title()

            return last_name, middle_name, first_name

        except:
            return None, None, None
