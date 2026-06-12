from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.io_utils import FIGURE_DIR, TABLE_DIR, ensure_dirs, first_column, infer_case_id, list_exports, read_comsol_table
from src.metrics import capillary_summary
from src.plotting import save_line


def main() -> int:
    ensure_dirs()
    files = list_exports(["*capillary*phase*.csv", "*capillary*phase*.txt", "*phasefield*.csv", "*phasefield*.txt"])
    if not files:
        print("No capillary phase-field exports found in data/exports.")
        return 0

    summaries = []
    for path in files:
        df = read_comsol_table(path)
        z_col = first_column(df, ["z", "y", "height", "arc_length", "coordinate"])
        phase_col = first_column(df, ["phase", "pf", "phi", "water_volume_fraction", "volume_fraction"])
        time_col = next((c for c in df.columns if "time" in c), None)
        channel_col = next((c for c in df.columns if "channel" in c or "line" in c or "probe" in c), None)
        out = capillary_summary(df, z_col, phase_col, time_col, channel_col)
        out.insert(0, "case_id", infer_case_id(path))
        out.insert(1, "source_file", str(path))
        summaries.append(out)

    result = summaries[0] if len(summaries) == 1 else __import__("pandas").concat(summaries, ignore_index=True)
    result.to_csv(TABLE_DIR / "capillary_phasefield_front_summary.csv", index=False)

    if "time" in result.columns and "mean" in result.columns:
        save_line(result, "time", "mean", FIGURE_DIR / "capillary_mean_rise_vs_time.png", hue="case_id", title="Mean Capillary Rise")
    print("wrote capillary_phasefield_front_summary.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
