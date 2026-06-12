from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.io_utils import EXPERIMENT_DIR, FIGURE_DIR, TABLE_DIR, ensure_dirs, first_column, infer_case_id, list_exports, read_comsol_table
from src.metrics import engineering_curve, initial_modulus
from src.plotting import save_line


DEFAULT_AREA_MM2 = 15.5 * 15.5
DEFAULT_HEIGHT_MM = 15.5


def dimensions_from_name(path: Path) -> tuple[float, float]:
    text = path.stem.lower()
    m = re.search(r"area([0-9.]+)", text)
    area = float(m.group(1)) if m else DEFAULT_AREA_MM2
    h = re.search(r"h([0-9.]+)", text)
    height = float(h.group(1)) if h else DEFAULT_HEIGHT_MM
    return area, height


def main() -> int:
    ensure_dirs()
    files = list_exports(["*force*.csv", "*force*.txt", "*stress*.csv", "*instron*.csv"])
    files += sorted(EXPERIMENT_DIR.glob("*instron*.csv"))
    if not files:
        print("No mechanical force-displacement exports found in data/exports or data/experimental.")
        return 0

    curves = []
    summary_rows = []
    for path in files:
        df = read_comsol_table(path)
        force_col = first_column(df, ["force", "reaction_force", "load", "load_n"])
        disp_col = first_column(df, ["displacement", "disp", "extension", "u", "u_z"])
        area, height = dimensions_from_name(path)
        curve = engineering_curve(df[force_col], df[disp_col], area, height)
        case_id = infer_case_id(path)
        curve.insert(0, "case_id", case_id)
        curve.insert(1, "source_file", str(path))
        curves.append(curve)
        row = {"case_id": case_id, "source_file": str(path), "area_mm2": area, "height_mm": height}
        row.update(initial_modulus(curve))
        row["peak_stress_kpa"] = float(curve["stress_kpa"].max())
        row["strain_at_peak"] = float(curve.loc[curve["stress_kpa"].idxmax(), "strain"])
        summary_rows.append(row)

    all_curves = pd.concat(curves, ignore_index=True)
    summary = pd.DataFrame(summary_rows)
    all_curves.to_csv(TABLE_DIR / "mechanical_engineering_stress_strain_curves.csv", index=False)
    summary.to_csv(TABLE_DIR / "mechanical_modulus_summary.csv", index=False)
    save_line(all_curves, "strain", "stress_kpa", FIGURE_DIR / "mechanical_stress_strain_curves.png", hue="case_id", title="Engineering Stress-Strain")
    print("wrote mechanical_modulus_summary.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
