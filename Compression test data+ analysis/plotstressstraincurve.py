import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

# ============================================================
# USER SETTINGS — PURE TPMS / NO BC
# ============================================================

files = [
    "pureBCtest1_1.csv",
    "pureBCtest2_1.csv",
    "pureBCtest3_1.csv"
]

sample_names = [
    "pureBCtest1",
    "pureBCtest2",
    "pureBCtest3"
]

material_name = "Pure BC"
structure_name = "None"
cell_size_label = "None"

# Sample dimensions
width_mm = 18.0
depth_mm = 18.0
height_mm = 20.0

cross_section_area_mm2 = width_mm * depth_mm

# Young's modulus fitting range
fit_strain_min = 0.05
fit_strain_max = 0.15

# Fixed plotting range
x_axis_min = 0.0
x_axis_max = 0.7
y_axis_min = 0.0
y_axis_max = 0.02


# ============================================================
# FUNCTION TO READ INSTRON CSV
# ============================================================

def read_instron_csv(filepath):
    df = pd.read_csv(filepath, skiprows=6)

    df = df.iloc[:, 1:4]
    df.columns = ["Time_s", "Displacement_mm", "Force_N"]

    df = df.apply(pd.to_numeric, errors="coerce").dropna()

    df["Displacement_mm"] = df["Displacement_mm"] - df["Displacement_mm"].iloc[0]
    df["Force_N"] = df["Force_N"] - df["Force_N"].iloc[:50].mean()

    df["Displacement_mm"] = abs(df["Displacement_mm"])
    df["Force_N"] = abs(df["Force_N"])

    df["Strain"] = df["Displacement_mm"] / height_mm
    df["Stress_MPa"] = df["Force_N"] / cross_section_area_mm2

    return df


# ============================================================
# READ DATA AND CALCULATE YOUNG'S MODULUS
# ============================================================

all_data = []
modulus_results = []

for file, name in zip(files, sample_names):
    df = read_instron_csv(file)
    all_data.append(df)

    fit_region = df[
        (df["Strain"] >= fit_strain_min) &
        (df["Strain"] <= fit_strain_max)
    ]

    slope, intercept, r_value, p_value, std_err = linregress(
        fit_region["Strain"],
        fit_region["Stress_MPa"]
    )

    modulus_results.append({
        "Sample": name,
        "Young's Modulus (MPa)": slope,
        "R²": r_value**2
    })


# ============================================================
# PLOT THREE PURE TPMS STRESS-STRAIN CURVES
# ============================================================

plt.figure(figsize=(8, 6))

for df, name in zip(all_data, sample_names):
    plt.plot(df["Strain"], df["Stress_MPa"], label=name)

plt.xlabel("Engineering Strain, ε")
plt.ylabel("Engineering Stress, σ (MPa)")
plt.title(
    f"Stress-Strain Curves of {material_name} {structure_name} Samples\n"
    f"Cell Size: {cell_size_label}, 3 Repeated Compression Tests"
)

plt.xlim(x_axis_min, x_axis_max)
plt.ylim(y_axis_min, y_axis_max)

plt.legend(title="Samples")
plt.grid(True)
plt.tight_layout()
plt.savefig("pureBCstress_strain_curves.png", dpi=300)
plt.show()


# ============================================================
# EXPORT YOUNG'S MODULUS RESULTS
# ============================================================

modulus_df = pd.DataFrame(modulus_results)

print("\nYoung's Modulus Results:")
print(modulus_df)

modulus_df.to_csv(
    "pureBCyoungs_modulus_results.csv",
    index=False
)


# ============================================================
# CREATE AVERAGED STRESS-STRAIN CURVE
# ============================================================

max_common_strain = min(df["Strain"].max() for df in all_data)

common_strain = np.linspace(0, max_common_strain, 1000)

interpolated_stresses = []

for df in all_data:
    stress_interp = np.interp(
        common_strain,
        df["Strain"],
        df["Stress_MPa"]
    )
    interpolated_stresses.append(stress_interp)

mean_stress = np.mean(interpolated_stresses, axis=0)
std_stress = np.std(interpolated_stresses, axis=0)

average_df = pd.DataFrame({
    "Strain": common_strain,
    "Average_Stress_MPa": mean_stress,
    "Stress_SD_MPa": std_stress
})

average_df.to_csv(
    "pureBC_average_stress_strain_curve.csv",
    index=False
)


# ============================================================
# PLOT AVERAGED PURE TPMS STRESS-STRAIN CURVE
# ============================================================

plt.figure(figsize=(8, 6))

plt.plot(
    common_strain,
    mean_stress,
    label="Average Stress-Strain Curve"
)

plt.fill_between(
    common_strain,
    mean_stress - std_stress,
    mean_stress + std_stress,
    alpha=0.2,
    label="±1 Standard Deviation"
)

plt.xlabel("Engineering Strain, ε")
plt.ylabel("Engineering Stress, σ (MPa)")
plt.title(
    f"Average Stress-Strain Curve of {material_name} {structure_name} Samples\n"
    f"Cell Size: {cell_size_label}, 3 Repeated Compression Tests"
)

plt.xlim(x_axis_min, x_axis_max)
plt.ylim(y_axis_min, y_axis_max)

plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("pureBC_average_stress_strain_curve.png", dpi=300)
plt.show()


# ============================================================
# OPTIONAL: EXPORT EACH INDIVIDUAL PURE TPMS CURVE
# ============================================================

for df, name in zip(all_data, sample_names):
    clean_name = (
        name.replace(" ", "_")
        .replace("-", "")
        .replace(".", "p")
        .replace("×", "x")
    )

    df[["Strain", "Stress_MPa"]].to_csv(
        f"{clean_name}_stress_strain_curve.csv",
        index=False
    )