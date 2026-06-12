# Model Evaluation Analysis Code

This folder contains the post-processing scripts used to analyse COMSOL simulation exports and guideline-evaluation data for the BNC-PHB scaffold thesis.

The scripts are designed around exported COMSOL tables rather than direct `.mph` interrogation. In COMSOL, export profile, cut-line, volume, or global evaluation tables as `.csv` or `.txt`, place them under `data/exports/`, and run the matching script.

## Folder Layout

```text
Model Evaluation/
  README.md
  requirements.txt
  run_all.py
  data/
    exports/
    experimental/
    generated_volumes/
  results/
    tables/
    figures/
  src/
    io_utils.py
    metrics.py
    plotting.py
  scripts/
    01_capillary_phasefield_analysis.py
    02_oxygen_penetration_analysis.py
    03_aspect_ratio_capillary_map.py
    04_mechanical_stress_strain_analysis.py
    05_guideline_model_evaluation.py
```

## Expected Export Types

- Capillary phase-field line profiles: columns similar to `time`, `channel`, `z`, `pf` or `phase`.
- Oxygen concentration profiles: columns similar to `time`, `z`, `c` or `oxygen_mg_L`.
- Aspect-ratio capillary exports: include `width_mm`, `depth_mm`, and either raw phase-field profiles or an exported `height_mm`.
- Mechanical COMSOL/Instron curves: columns similar to `displacement_mm`, `force_N`, plus specimen dimensions.
- Generated design volumes: binary `.npy` volumes or 2D/3D image masks where solid is non-zero.

## Notes

The analysis uses the thesis thresholds:

- Capillary front: phase-field threshold = `0.5`.
- Oxygen sufficiency threshold = `3.1 mg/L`.
- Guideline screen: channel width >= `1.5 mm`, wall thickness >= `0.50 mm`, solid fraction >= `0.15`.
- Mechanical modulus: initial linear engineering stress-strain region, default `0.02-0.08` strain.

The scripts write tables to `results/tables/` and figures to `results/figures/`.
