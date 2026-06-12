import numpy as np
from scipy.stats import pearsonr

# ── Data ──────────────────────────────────────────────────────────────────
E0  = np.array([37.8, 16.6, 17.7, 18.7, 16.6, 102.4, 13.0])  # kPa
phi = np.array([0.080, 0.054, 0.047, 0.040, 0.056, 0.080, 0.038])
t   = np.array([0.25, 0.25, 0.25, 0.25, 0.35, 0.50, 0.25])   # mm
L   = np.array([3.00, 4.50, 5.17, 6.00, 6.00, 6.00, 6.33])   # mm

# ── 1. Pearson Correlations ────────────────────────────────────────────────
for label, param in [("φ", phi), ("t", t), ("L", L),
                     ("φ²", phi**2), ("t³", t**3)]:
    r, p = pearsonr(param, E0)
    print(f"{label}: r={r:+.3f}, p={p:.4f}")

# ── 2. Power-law fit: E0 = A * phi^n ──────────────────────────────────────
coeffs  = np.polyfit(np.log(phi), np.log(E0), 1)
n, ln_A = coeffs
A       = np.exp(ln_A)
E_pred  = A * phi**n
R2      = 1 - np.sum((E0 - E_pred)**2) / np.sum((E0 - np.mean(E0))**2)
print(f"E0 = {A:.0f} × φ^{n:.2f},  R² = {R2:.3f}")

# ── 3. t³ scaling extrapolation ───────────────────────────────────────────
E0_ref, t_ref = 18.7, 0.25
for t_new in [0.35, 0.40, 0.50, 0.60, 0.75, 1.00]:
    print(f"t={t_new:.2f}mm → E0 ≈ {E0_ref * (t_new/t_ref)**3:.0f} kPa")

# ── 4. Gibson–Ashby target inversion ──────────────────────────────────────
C_Es = np.median(E0 / phi**2)          # kPa
print(f"Median C·Es = {C_Es:.0f} kPa")
for E_target in [130, 500, 1000, 2840]:
    phi_req = np.sqrt(E_target / C_Es)
    print(f"E0={E_target} kPa → φ = {phi_req:.3f}, porosity = {(1-phi_req)*100:.1f}%")