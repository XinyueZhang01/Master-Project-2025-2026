from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.io_utils import FIGURE_DIR, TABLE_DIR, ensure_dirs, first_column, infer_case_id, list_exports, read_comsol_table
from src.metrics import oxygen_metrics
from src.plotting import save_line


OXYGEN_THRESHOLD_MG_L = 3.1


def main() -> int:
    ensure_dirs()
    files = list_exports(["*oxygen*.csv", "*oxygen*.txt", "*diffusion*.csv", "*diffusion*.txt", "*concentration*.csv"])
    if not files:
        print("No oxygen concentration exports found in data/exports.")
        return 0

    summaries = []
    for path in files:
        df = read_comsol_table(path)
        z_col = first_column(df, ["z", "depth", "y", "coordinate", "arc_length"])
        c_col = first_column(df, ["oxygen", "concentration", "c", "tds_c", "mg_l"])
        time_col = next((c for c in df.columns if "time" in c), None)
        out = oxygen_metrics(df, z_col, c_col, time_col, threshold=OXYGEN_THRESHOLD_MG_L)
        out.insert(0, "case_id", infer_case_id(path))
        out.insert(1, "source_file", str(path))
        summaries.append(out)

    result = pd.concat(summaries, ignore_index=True)
    result.to_csv(TABLE_DIR / "oxygen_penetration_summary.csv", index=False)

    time_cols = [c for c in result.columns if "time" in c]
    if time_cols:
        save_line(
            result,
            time_cols[0],
            "penetration_depth_mm",
            FIGURE_DIR / "oxygen_penetration_depth_vs_time.png",
            hue="case_id",
            title="Oxygen Penetration Depth Above 3.1 mg/L",
        )
    print("wrote oxygen_penetration_summary.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
