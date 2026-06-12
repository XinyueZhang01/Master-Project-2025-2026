from __future__ import annotations

from pathlib import Path

import pandas as pd


STYLE = {
    "Research": "#2563EB",
    "Simulation": "#0F766E",
    "Experimental": "#16A34A",
    "Analysis": "#EA580C",
    "Writing": "#334155",
}


def save_line(df: pd.DataFrame, x: str, y: str, path: Path, hue: str | None = None, title: str | None = None) -> None:
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        print(f"matplotlib not installed; skipped figure {path.name}")
        return

    fig, ax = plt.subplots(figsize=(6.4, 4.0), dpi=220)
    if hue and hue in df.columns:
        for key, sub in df.groupby(hue):
            ax.plot(sub[x], sub[y], marker="o", linewidth=1.8, label=str(key))
        ax.legend(frameon=False, fontsize=8)
    else:
        ax.plot(df[x], df[y], marker="o", linewidth=1.8)
    ax.set_xlabel(x.replace("_", " "))
    ax.set_ylabel(y.replace("_", " "))
    ax.set_title(title or y.replace("_", " ").title())
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def save_bar(df: pd.DataFrame, x: str, y: str, path: Path, title: str | None = None) -> None:
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        print(f"matplotlib not installed; skipped figure {path.name}")
        return

    fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=220)
    ax.bar(df[x].astype(str), df[y], color="#0F766E")
    ax.set_xlabel(x.replace("_", " "))
    ax.set_ylabel(y.replace("_", " "))
    ax.set_title(title or y.replace("_", " ").title())
    ax.tick_params(axis="x", rotation=35)
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
