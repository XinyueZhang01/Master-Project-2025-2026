# Master Project 2025-2026

This repository contains computational models, generated scaffold evaluation code, COMSOL/MATLAB model-generation scripts, and experimental compression-test data used for the master project on geometry-based design guidelines for BNC-PHB scaffold growth.

The project combines simulation, generated geometry screening, and mechanical testing to evaluate how scaffold architecture affects capillary infiltration, oxygen transport, and compressive behaviour.

## Repository Structure

| Folder | Description |
|---|---|
| `Compression test data+ analysis/` | Instron compression-test CSV files, processed stress-strain curves, Young's modulus summaries, and Python scripts for mechanical data analysis. |
| `generatevolumesforevaluation/` | VAE-based 2D scaffold generation, geometric guideline screening, 3D volume generation, 3D evaluation, selected-volume processing, and STEP conversion tools. |
| `MATLAB+COMSOL model generation/` | MATLAB scripts exported from COMSOL LiveLink, plus batch COMSOL topology-evaluation code. |
| `Model Evaluation/` | Python package for post-processing COMSOL-exported tables and evaluating capillary, oxygen, mechanical, and guideline metrics. |

## Main Workflows

### 1. COMSOL / MATLAB Model Generation

COMSOL LiveLink-exported MATLAB files build and run capillary phase-field simulations and related model exports. These scripts preserve the COMSOL model state and allow models to be regenerated or modified from MATLAB.

### 2. Compression-Test Analysis

Instron CSV files are processed into engineering stress-strain curves. Young's modulus is estimated from a user-defined initial strain region, and replicate curves are plotted and averaged.

### 3. Generated Volume Evaluation

A pretrained VAE generates 2D binary scaffold designs. Designs are screened using geometric rules such as minimum channel width and wall thickness, then selected designs are interpolated into 3D volumes and evaluated by solid fraction, porosity, wall thickness, and composite guideline score.

### 4. Model Evaluation

COMSOL exports are post-processed using Python to compute capillary rise, oxygen penetration depth, depleted oxygen fraction, mechanical modulus, and guideline pass/fail classification.

## Requirements

Different folders require different software:

- Python 3.9+
- MATLAB
- COMSOL Multiphysics
- COMSOL LiveLink for MATLAB
- Common Python packages:
  - `numpy`
  - `pandas`
  - `matplotlib`
  - `scipy`
  - `scikit-image`
  - `torch`, for VAE-based generation
  - `cadquery`, for STEP conversion
  - `pyvista`, for 3D volume viewing

Install only the packages needed for the folder you are running.

## Notes

- Some scripts contain absolute Windows paths from the original working machine, especially paths under `D:\BaiduNetdiskDownload`. Update these paths before running elsewhere.
- Several COMSOL MATLAB files are exported scripts, so they are intentionally verbose.
- Generated model files, raw simulation exports, and large `.mph` files may not be stored in the repository because of size limits.
- The repository is best read as a research-code archive rather than a polished software package.

## Suggested README Order

For understanding the project, read the folder READMEs in this order:

1. `generatevolumesforevaluation/`
2. `Model Evaluation/`
3. `Compression test data+ analysis/`
4. `MATLAB+COMSOL model generation/`

