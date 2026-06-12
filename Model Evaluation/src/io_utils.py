from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "data" / "exports"
EXPERIMENT_DIR = ROOT / "data" / "experimental"
VOLUME_DIR = ROOT / "data" / "generated_volumes"
TABLE_DIR = ROOT / "results" / "tables"
FIGURE_DIR = ROOT / "results" / "figures"


def ensure_dirs() -> None:
    for path in [EXPORT_DIR, EXPERIMENT_DIR, VOLUME_DIR, TABLE_DIR, FIGURE_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def list_exports(patterns: Iterable[str]) -> list[Path]:
    files: list[Path] = []
    for pattern in patterns:
        files.extend(EXPORT_DIR.glob(pattern))
    return sorted(set(files))


def clean_name(name: str) -> str:
    name = re.sub(r"\s*\(.*?\)", "", str(name))
    name = name.strip().lower()
    name = name.replace("%", "").replace("/", "_per_")
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def read_comsol_table(path: Path) -> pd.DataFrame:
    """Read a COMSOL CSV/TXT export with comment lines and inconsistent delimiters."""
    path = Path(path)
    text = path.read_text(errors="ignore")
    lines = [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith(("%", "#"))]
    if not lines:
        raise ValueError(f"No tabular data found in {path}")

    sample = "\n".join(lines[:12])
    sep = "," if sample.count(",") >= sample.count("\t") else "\t"
    if sep == "\t" and sample.count("\t") == 0:
        sep = r"\s+"

    from io import StringIO

    df = pd.read_csv(StringIO("\n".join(lines)), sep=sep, engine="python")
    df.columns = [clean_name(c) for c in df.columns]
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")
    df.attrs["source_file"] = str(path)
    return df


def first_column(df: pd.DataFrame, candidates: Iterable[str]) -> str:
    lookup = {clean_name(c): c for c in df.columns}
    for candidate in candidates:
        key = clean_name(candidate)
        if key in lookup:
            return lookup[key]
    for col in df.columns:
        c = clean_name(col)
        if any(clean_name(candidate) in c for candidate in candidates):
            return col
    raise KeyError(f"None of {list(candidates)} found in columns: {list(df.columns)}")


def infer_case_id(path: Path) -> str:
    stem = Path(path).stem
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem)
    return stem


def load_npy_or_image(path: Path) -> np.ndarray:
    path = Path(path)
    if path.suffix.lower() == ".npy":
        arr = np.load(path)
    else:
        from skimage.io import imread

        arr = imread(path)
    if arr.ndim > 3:
        arr = arr[..., 0]
    return arr > 0
