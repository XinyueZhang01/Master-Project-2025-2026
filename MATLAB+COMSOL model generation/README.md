# MATLAB + COMSOL Model Generation

This folder contains MATLAB scripts used to generate, run, and export COMSOL Multiphysics models for the master project. The files are primarily COMSOL LiveLink for MATLAB exports, together with a batch-processing script for topology-based model evaluation.

The models support simulation-led screening of scaffold geometries, including capillary two-phase flow, phase-field interface tracking, model animation/export, and topology-dependent solid mechanics/dispersion analysis.

## Contents

| File | Purpose |
|---|---|
| `Final parameter sweep.m` | Compact COMSOL-exported MATLAB model for a 2D two-phase capillary/phase-field simulation. It creates the model, geometry, mesh, laminar flow and phase-field physics, transient study, and animation export. |
| `firsttest.m` | Full COMSOL-exported development model. This appears to include extended model setup, result plots, animations, image exports, and exploratory post-processing. |
| `newone.m` | Later COMSOL-exported version of the same model family, including additional result export definitions. |
| `testwithmatlab.m` | Smaller COMSOL-exported test model for checking the MATLAB-COMSOL workflow. |
| `testwithmatlab1.m` | Extended exported model similar to `newone.m`, including multiple result plot groups, animations, image exports, and data exports. |
| `topology.m` | Batch MATLAB script that loads `topology.mph`, assigns material parameters and topology selections from Excel data, runs the COMSOL study, and exports dispersion-curve results to CSV. |

## Requirements

- MATLAB
- COMSOL Multiphysics
- COMSOL LiveLink for MATLAB
- Required COMSOL modules for the exported physics interfaces, including:
  - Laminar Flow
  - Phase Field
  - Two-Phase Flow, Phase Field
  - Solid Mechanics, for `topology.m`

The scripts were exported from COMSOL `6.3.0.290`, so the most reproducible environment is COMSOL 6.3 with a compatible MATLAB release.

## Model Families

### Capillary and Phase-Field Models

The COMSOL-exported scripts build 2D capillary-rise models using:

- `LaminarFlow`
- `PhaseField`
- `TwoPhaseFlowPhaseField`
- transient studies
- phase initialization
- result plot groups and animation exports

These models are intended for evaluating liquid-air interface movement through scaffold-like channel geometries. The phase-field output can be exported from COMSOL and post-processed separately to extract capillary front height, mean rise, and inter-channel variation.

### Topology / Dispersion Batch Model

`topology.m` performs a batch workflow:

1. Reads binary topology images and material parameters from Excel files under `integrated_images/`.
2. Loads an existing COMSOL model, `topology.mph`.
3. Updates material parameters:
   - `Es`
   - `Ps`
   - `rhos`
4. Selects solid domains according to the binary topology image.
5. Runs `std1`.
6. Exports a dispersion curve as CSV into `dispersion_curves/`.
7. Logs progress or failed cases into `processing/` and `errors/`.

## Expected Folder Structure

Some scripts contain absolute paths from the original development machine, such as `D:\BaiduNetdiskDownload`. Before running on another machine, update these paths or run the scripts from a matching directory structure.

For `topology.m`, the expected local structure is:

```text
MATLAB+COMSOL model generation/
  topology.m
  topology.mph
  integrated_images/
    0.xlsx
  dispersion_curves/
  processing/
  errors/
```

The Excel file is expected to contain at least:

- sheet `images`: binary topology image data
- sheet `soil_parameters`: material parameters used to update the COMSOL model

## Typical Usage

### Run a COMSOL-exported MATLAB model

Open MATLAB with COMSOL LiveLink enabled, then run one of the exported model files:

```matlab
model = model;
```

Because several files define the same MATLAB function name, `model`, run them one at a time from their own working context or rename the function/file before combining them in a larger workflow.

### Run the topology batch script

```matlab
topology
```

Before running:

- ensure `topology.mph` exists in the working directory
- create `dispersion_curves/`, `processing/`, and `errors/` if they do not already exist
- confirm the Excel input path and sheet names are correct
- check that the selected index range at the top of `topology.m` matches the cases to process

## Outputs

Depending on the script, outputs may include:

- COMSOL animations, such as `.gif`
- exported images, such as `.png`
- exported plot/data tables, such as `.csv`
- processed dispersion curves
- error `.mph` files saved for failed batch cases

Several exported model scripts currently write to absolute paths. These should be changed before running on a different machine.

## Notes for Reproducibility

- These files are generated or semi-generated MATLAB scripts from COMSOL, so they are verbose by design.
- The exported scripts preserve the model state at the time of export but are not yet refactored into reusable functions.
- For publication-quality reproducibility, recommended next steps are:
  - replace hard-coded absolute paths with configurable variables
  - rename scripts so each has a unique function name
  - add a `config.m` file for input/output folders
  - save key COMSOL exports as CSV for downstream Python/MATLAB analysis
  - document COMSOL version, mesh settings, solver settings, and exported result variables for each simulation case

## Project Context

These model-generation scripts belong to the master project repository:

`Master-Project-2025-2026`

They support computational model generation and screening workflows used alongside experimental scaffold fabrication, growth monitoring, and mechanical evaluation.
