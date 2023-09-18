import logging
import os
from pathlib import Path

import numpy as np

from lm_datasets.datasets.base import Availability
from lm_datasets.datasets.jsonl_dataset import JSONLDataset


logger = logging.getLogger(__name__)


DEFAULT_OSCAR_MIN_HARMFUL_PP = 20.0

"""
'colossal_oscar_05-06-23_bg,colossal_oscar_05-06-23_cs,colossal_oscar_05-06-23_da,colossal_oscar_05-06-23_el,colossal_oscar_05-06-23_et,colossal_oscar_05-06-23_fi,colossal_oscar_05-06-23_fr,colossal_oscar_05-06-23_ga,colossal_oscar_05-06-23_hr,colossal_oscar_05-06-23_hu,colossal_oscar_05-06-23_lt,colossal_oscar_05-06-23_lv,colossal_oscar_05-06-23_mt,colossal_oscar_05-06-23_nl,colossal_oscar_05-06-23_pl,colossal_oscar_05-06-23_pt,colossal_oscar_05-06-23_ro,colossal_oscar_05-06-23_sk,colossal_oscar_05-06-23_sl,colossal_oscar_05-06-23_sv,colossal_oscar_05-06-23_uk,colossal_oscar_05-06-23_sr,colossal_oscar_05-06-23_sh,colossal_oscar_05-06-23_nn,colossal_oscar_05-06-23_no,colossal_oscar_05-06-23_eu,colossal_oscar_05-06-23_ca,colossal_oscar_05-06-23_gl,colossal_oscar_03-04-23_bg,colossal_oscar_03-04-23_cs,colossal_oscar_03-04-23_da,colossal_oscar_03-04-23_el,colossal_oscar_03-04-23_et,colossal_oscar_03-04-23_fi,colossal_oscar_03-04-23_fr,colossal_oscar_03-04-23_ga,colossal_oscar_03-04-23_hr,colossal_oscar_03-04-23_hu,colossal_oscar_03-04-23_lt,colossal_oscar_03-04-23_lv,colossal_oscar_03-04-23_mt,colossal_oscar_03-04-23_nl,colossal_oscar_03-04-23_pl,colossal_oscar_03-04-23_pt,colossal_oscar_03-04-23_ro,colossal_oscar_03-04-23_sk,colossal_oscar_03-04-23_sl,colossal_oscar_03-04-23_sv,colossal_oscar_03-04-23_uk,colossal_oscar_03-04-23_sr,colossal_oscar_03-04-23_sh,colossal_oscar_03-04-23_nn,colossal_oscar_03-04-23_no,colossal_oscar_03-04-23_eu,colossal_oscar_03-04-23_ca,colossal_oscar_03-04-23_gl'
"""  # noqa
OSCAR_DUMPS = ["05-06-23", "03-04-23"]
LANGUAGES = "bg cs da el et fi ga hr hu lt lv mt nl pl pt ro sk sl sv uk sr sh nn no eu ca gl".split(" ")  # removed fr

EXCLUDE_CATEGORIES = {
    # See http://dsi.ut-capitole.fr/blacklists/index_en.php
    "agressif",
    "adult",
    "cryptojacking",
    "dangerous_material",
    "phishing",
    "warez",
}


class ColossalOscarBaseDataset(JSONLDataset):
    """
    Read OSCAR output from jsonl.zst files (as provided on HF)
    """

    SOURCE_ID = "colossal_oscar"

    DESCRIPTION = "Colossal OSCAR 1"
    HOMEPAGE = "https://huggingface.co/datasets/oscar-corpus/colossal-oscar-1.0"
    AVAILIBILITY = Availability.SIGNIN_DOWNLOAD

    LOCAL_DIRS = ["pegasus:/netscratch/mostendorff/experiments/eulm/data/colossal-oscar-1.0"]

    DATASET_ID = "colossal_oscar_05-06-23_da"
    LANGUAGES = ["da"]
    DUMP_VERSION = "05-06-23"

    min_harmful_pp = None

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # set min_harmful_pp

        # TODO hard coded
        # resources_dir = os.path.join("/netscratch/mostendorff/experiments/eulm", "resources", "oscar")

        # with open(os.path.join(resources_dir, "adult_pp_dict.pkl"), "rb") as f:
        #     c_dict_means = pickle.load(f)

        # with open(os.path.join(resources_dir, "adult_pp_dict_full.pkl"), "rb") as file:
        #     # Mean perplexity for documents with the Adult quality warning in the Oscar Dataset
        #     dict_full = pickle.load(file)

        dict_full = {}

        self.min_harmful_pp = (
            np.mean(dict_full[self.get_language_code()])
            if self.get_language_code() in dict_full
            else DEFAULT_OSCAR_MIN_HARMFUL_PP
        )

        logger.info(f"{self.min_harmful_pp=}")

    def get_text_from_item(self, doc):
        if doc["metadata"]["quality_warnings"]:
            self.counter.update({"filtered_quality_warnings": 1})
            return None
        elif (
            "harmful_pp" in doc["metadata"]
            and doc["metadata"]["harmful_pp"]
            and doc["metadata"]["harmful_pp"] < self.min_harmful_pp
        ):
            self.counter.update({"filtered_harmful_pp": 1})
            return None
        elif doc["metadata"]["categories"] and len(set(doc["metadata"]["categories"]) & EXCLUDE_CATEGORIES) > 0:
            self.counter.update({"filtered_categories": 1})
            return None
        else:
            return doc["content"]

    def get_raw_jsonl_paths(self):
        lang = self.get_language_code()
        dataset_path = Path(os.path.join(self.get_local_dataset_dir(), self.DUMP_VERSION, f"{lang}_meta"))

        return sorted([str(p) for p in dataset_path.glob("*.jsonl.zst")])

    def get_bytes(self):
        return sum(os.stat(fp).st_size for fp in self.get_raw_jsonl_paths())


def get_colossal_oscar_class(lang, dump_version):
    class ColossalOscarDataset(ColossalOscarBaseDataset):
        DATASET_ID = f"colossal_oscar_{dump_version}_{lang}"
        LANGUAGES = [lang]
        DUMP_VERSION = dump_version

    return ColossalOscarDataset


def get_colossal_oscar_auto_classes():
    """
    Auto generate dataset classes
    """

    return [get_colossal_oscar_class(lang, dump_version) for dump_version in OSCAR_DUMPS for lang in LANGUAGES]
