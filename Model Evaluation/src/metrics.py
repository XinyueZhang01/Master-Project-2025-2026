from __future__ import annotations

import numpy as np
import pandas as pd


def interface_height_from_profile(z: np.ndarray, phase: np.ndarray, threshold: float = 0.5) -> float:
    """Return the deepest vertical coordinate where the liquid phase exceeds threshold."""
    z = np.asarray(z, dtype=float)
    phase = np.asarray(phase, dtype=float)
    mask = np.isfinite(z) & np.isfinite(phase)
    if not np.any(mask):
        return np.nan
    z, phase = z[mask], phase[mask]
    wet = phase >= threshold
    if not np.any(wet):
        return np.nan
    return float(np.nanmax(z[wet]))


def capillary_summary(df: pd.DataFrame, z_col: str, phase_col: str, time_col: str | None, channel_col: str | None) -> pd.DataFrame:
    group_cols = [c for c in [time_col, channel_col] if c]
    if not group_cols:
        height = interface_height_from_profile(df[z_col], df[phase_col])
        return pd.DataFrame([{"height_mm": height}])
    rows = []
    for keys, sub in df.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = dict(zip(group_cols, keys))
        row["height_mm"] = interface_height_from_profile(sub[z_col], sub[phase_col])
        rows.append(row)
    out = pd.DataFrame(rows)
    if time_col and channel_col:
        spread = out.groupby(time_col)["height_mm"].agg(["mean", "min", "max", "std"]).reset_index()
        spread["delta_h_mm"] = spread["max"] - spread["min"]
        out = out.merge(spread[[time_col, "mean", "delta_h_mm"]], on=time_col, how="left")
    return out


def oxygen_metrics(df: pd.DataFrame, z_col: str, c_col: str, time_col: str | None, threshold: float = 3.1) -> pd.DataFrame:
    rows = []
    groups = df.groupby(time_col, dropna=False) if time_col else [(None, df)]
    for t, sub in groups:
        z = pd.to_numeric(sub[z_col], errors="coerce").to_numpy(float)
        c = pd.to_numeric(sub[c_col], errors="coerce").to_numpy(float)
        valid = np.isfinite(z) & np.isfinite(c)
        z, c = z[valid], c[valid]
        if len(z) == 0:
            continue
        above = c >= threshold
        penetration = float(np.nanmax(z[above])) if np.any(above) else 0.0
        lower_cut = np.nanquantile(z, 0.75)
        lower_min = float(np.nanmin(c[z >= lower_cut])) if np.any(z >= lower_cut) else float(np.nanmin(c))
        depleted_fraction = float(np.mean(c < threshold))
        row = {
            "penetration_depth_mm": penetration,
            "min_lower_region_mg_L": lower_min,
            "oxygen_depleted_fraction": depleted_fraction,
            "mean_oxygen_mg_L": float(np.nanmean(c)),
        }
        if time_col:
            row[time_col] = t
        rows.append(row)
    return pd.DataFrame(rows)


def engineering_curve(force_n: np.ndarray, displacement_mm: np.ndarray, area_mm2: float, height_mm: float) -> pd.DataFrame:
    force_n = np.asarray(force_n, dtype=float)
    displacement_mm = np.asarray(displacement_mm, dtype=float)
    strain = np.abs(displacement_mm) / height_mm
    stress_kpa = np.abs(force_n) / area_mm2 * 1000.0
    return pd.DataFrame({"strain": strain, "stress_kpa": stress_kpa})


def initial_modulus(curve: pd.DataFrame, low: float = 0.02, high: float = 0.08) -> dict[str, float]:
    sub = curve[(curve["strain"] >= low) & (curve["strain"] <= high)].dropna()
    if len(sub) < 3:
        sub = curve[curve["strain"] <= high].dropna()
    if len(sub) < 3:
        return {"E_kPa": np.nan, "fit_r2": np.nan, "fit_n": len(sub)}
    x = sub["strain"].to_numpy(float)
    y = sub["stress_kpa"].to_numpy(float)
    slope, intercept = np.polyfit(x, y, 1)
    pred = slope * x + intercept
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot else np.nan
    return {"E_kPa": float(slope), "fit_intercept_kpa": float(intercept), "fit_r2": float(r2), "fit_n": int(len(sub))}


def binary_geometry_metrics(mask: np.ndarray, voxel_mm: float = 0.1) -> dict[str, float]:
    try:
        from scipy.ndimage import distance_transform_edt
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "scipy is required for EDT-based geometry metrics. Install requirements.txt or run this script in an environment with scipy."
        ) from exc

    solid = np.asarray(mask).astype(bool)
    void = ~solid
    solid_fraction = float(np.mean(solid))
    porosity = 1.0 - solid_fraction

    solid_dt = distance_transform_edt(solid) * voxel_mm
    void_dt = distance_transform_edt(void) * voxel_mm
    wall_thickness_mm = float(2.0 * np.percentile(solid_dt[solid_dt > 0], 5)) if np.any(solid_dt > 0) else 0.0
    min_channel_width_mm = float(2.0 * np.percentile(void_dt[void_dt > 0], 5)) if np.any(void_dt > 0) else 0.0
    return {
        "solid_fraction": solid_fraction,
        "porosity": porosity,
        "wall_thickness_mm": wall_thickness_mm,
        "min_channel_width_mm": min_channel_width_mm,
    }


def minmax(series: pd.Series) -> pd.Series:
    lo, hi = series.min(), series.max()
    if not np.isfinite(lo) or not np.isfinite(hi) or hi == lo:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - lo) / (hi - lo)
