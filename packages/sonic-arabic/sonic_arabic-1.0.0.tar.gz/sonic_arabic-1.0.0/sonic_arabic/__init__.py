import os
import pathlib

from sonic_arabic.utils_arabic.download_model import ensure_file_downloaded


cur_dir = pathlib.Path(__file__).parent.resolve()
path_to_punctuation_model = f"{cur_dir}/punctuation/BertPuncCap/models/mbert_base_cased_8langs"
ppm = path_to_punctuation_model


def initialize():
    ensure_file_downloaded(
        os.path.join(ppm, "config.yaml"),
        "https://drive.google.com/uc?export=download&id=1zB_etELwrgzSl-oZiN34607xpdhGohp1")

    ensure_file_downloaded(
        os.path.join(ppm, "best.ckpt"),
        "https://drive.google.com/uc?export=download&id=12WFBFswOfzdvW4pXSFtS9TAOPyTmZiGa&confirm=t&uuid=7cdedcae-e99e-4ca8-a46a-2057f9b8417a")


initialize()
