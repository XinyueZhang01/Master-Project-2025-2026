from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.io_utils import FIGURE_DIR, TABLE_DIR, VOLUME_DIR, ensure_dirs, infer_case_id, load_npy_or_image
from src.metrics import binary_geometry_metrics, minmax
from src.plotting import save_bar


VOXEL_MM = 0.1
MIN_CHANNEL_WIDTH_MM = 1.5
MIN_WALL_THICKNESS_MM = 0.50
MIN_SOLID_FRACTION = 0.15


def main() -> int:
    ensure_dirs()
    files = sorted(
        list(VOLUME_DIR.glob("*.npy"))
        + list(VOLUME_DIR.glob("*.png"))
        + list(VOLUME_DIR.glob("*.tif"))
        + list(VOLUME_DIR.glob("*.tiff"))
    )
    if not files:
        print("No generated binary volumes or masks found in data/generated_volumes.")
        return 0

    rows = []
    for path in files:
        mask = load_npy_or_image(path)
        metrics = binary_geometry_metrics(mask, voxel_mm=VOXEL_MM)
        metrics["case_id"] = infer_case_id(path)
        metrics["source_file"] = str(path)
        rows.append(metrics)

    df = pd.DataFrame(rows)
    df["passes_channel_width"] = df["min_channel_width_mm"] >= MIN_CHANNEL_WIDTH_MM
    df["passes_wall_thickness"] = df["wall_thickness_mm"] >= MIN_WALL_THICKNESS_MM
    df["passes_solid_fraction"] = df["solid_fraction"] >= MIN_SOLID_FRACTION
    df["guideline_class"] = df[["passes_channel_width", "passes_wall_thickness", "passes_solid_fraction"]].all(axis=1).map({True: "pass", False: "fail"})
    df["score"] = 0.93 * minmax(df["wall_thickness_mm"]) + 0.76 * minmax(df["solid_fraction"])
    df = df.sort_values("score", ascending=False)
    df.to_csv(TABLE_DIR / "guideline_model_evaluation_summary.csv", index=False)
    save_bar(df.head(20), "case_id", "score", FIGURE_DIR / "guideline_top20_scores.png", title="Top Guideline Scores")
    print("wrote guideline_model_evaluation_summary.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
