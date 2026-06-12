from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.io_utils import FIGURE_DIR, TABLE_DIR, ensure_dirs, first_column, list_exports, read_comsol_table


def main() -> int:
    ensure_dirs()
    files = list_exports(["*aspect*.csv", "*aspect*.txt", "*width*depth*.csv", "*capillary_map*.csv"])
    if not files:
        print("No aspect-ratio capillary exports found in data/exports.")
        return 0

    frames = []
    for path in files:
        df = read_comsol_table(path)
        width = first_column(df, ["width_mm", "width", "channel_width"])
        depth = first_column(df, ["depth_mm", "depth", "channel_depth"])
        try:
            height = first_column(df, ["height_mm", "rise_height", "capillary_rise", "h"])
            out = df[[width, depth, height]].copy()
            out.columns = ["width_mm", "depth_mm", "rise_height_mm"]
        except KeyError:
            print(f"Skipping {path}: no exported rise-height column. Run phase-field analysis first.")
            continue
        out["aspect_ratio"] = out["depth_mm"] / out["width_mm"]
        out["source_file"] = str(path)
        frames.append(out)

    if not frames:
        return 0
    result = pd.concat(frames, ignore_index=True)
    result.to_csv(TABLE_DIR / "aspect_ratio_capillary_map.csv", index=False)

    try:
        import matplotlib.pyplot as plt

        pivot = result.pivot_table(index="depth_mm", columns="width_mm", values="rise_height_mm", aggfunc="mean")
        fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=220)
        im = ax.imshow(pivot.values, aspect="auto", origin="lower", cmap="viridis")
        ax.set_xticks(range(len(pivot.columns)), [f"{x:g}" for x in pivot.columns], rotation=45)
        ax.set_yticks(range(len(pivot.index)), [f"{y:g}" for y in pivot.index])
        ax.set_xlabel("channel width (mm)")
        ax.set_ylabel("channel depth (mm)")
        ax.set_title("Capillary Rise Across Width-Depth Design Space")
        fig.colorbar(im, ax=ax, label="rise height (mm)")
        fig.tight_layout()
        fig.savefig(FIGURE_DIR / "aspect_ratio_capillary_heatmap.png")
        plt.close(fig)
    except ModuleNotFoundError:
        print("matplotlib not installed; skipped aspect-ratio heatmap")
    print("wrote aspect_ratio_capillary_map.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
