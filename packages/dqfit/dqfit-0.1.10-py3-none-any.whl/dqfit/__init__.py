import os
import pandas as pd
from pathlib import Path
from typing import List
from glob import glob

# from dotenv import find_dotenv, load_dotenv

# load_dotenv(find_dotenv())

from dqfit.dimensions import Complete, Conformant, Longitudinal, Plausible, Current
from dqfit.io import (
    get_bundle_paths,
    load_context,
    load_reference,
    read_bundle_resources,
    read_fhir,
    detect_fhir_resources,
)
from dqfit.model import Index
from dqfit.transform import transform_to_fhir_path
from dqfit.visualize import draw_population_path_dimensions, highlight_cells

PACKAGE_BASE = Path(__file__).parent.absolute()
MAX_CONCURRENCY = int(os.environ.get("MAX_CONCURRENCY", 10))


fhir_base = os.environ.get("FHIR_BASE", f"{PACKAGE_BASE}/data/synthetic")


def list_contexts():
    return [
        p.split("/")[-1].replace(".json", "").lower()
        for p in glob(f"{PACKAGE_BASE}/data/context/*")
    ]


__all__ = [
    "Index",
    "Conformant",
    "Complete",
    "Plausible",
    "Current",
    "Longitudinal",
    "transform_to_fhir_path",
    "read_fhir",
    "detect_fhir_resources",
    "read_bundle_resources",
    "get_bundle_paths",
    "load_context",
    "list_contexts",
    "draw_population_path_dimensions",
    "highlight_cells"
]
