from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    "01_capillary_phasefield_analysis.py",
    "02_oxygen_penetration_analysis.py",
    "03_aspect_ratio_capillary_map.py",
    "04_mechanical_stress_strain_analysis.py",
    "05_guideline_model_evaluation.py",
]


def main() -> int:
    for script in SCRIPTS:
        path = ROOT / "scripts" / script
        print(f"\n=== running {script} ===")
        result = subprocess.run([sys.executable, str(path)], cwd=ROOT)
        if result.returncode != 0:
            print(f"warning: {script} exited with code {result.returncode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
