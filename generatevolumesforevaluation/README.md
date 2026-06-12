# Generate Volumes for Evaluation

This folder contains the pipeline for generating scaffold geometries, screening them against design guidelines, assembling 3D volumes, evaluating geometric metrics, and preparing selected volumes for simulation.

The workflow supports the model-evaluation part of the project, where generated candidate structures are classified as guideline-compliant or non-compliant before mechanical simulation.

## Pipeline Overview

```text
Pretrained VAE
   |
   v
2D binary scaffold designs
   |
   v
EDT-based geometric screening
   |
   v
Pass/fail 2D design pools
   |
   v
Latent-space interpolation into 3D volumes
   |
   v
3D metric evaluation and ranking
   |
   v
Best/worst subset selection
   |
   v
Downsampling, island removal, viewing, and STEP conversion
```

## Main Scripts

### `screen_and_generate.py`

Generates 2D binary scaffold designs from a pretrained VAE and screens them using geometric rules.

Metrics:

- minimum channel width
- minimum wall thickness

Default physical scale:

- `384 x 384 px = 15 mm x 15 mm`
- minimum channel width threshold: `1.5 mm`
- minimum wall thickness threshold: `0.5 mm`

Typical output:

```text
output_dir/
  all/png/
  all/npy/
  passed/png/
  passed/npy/
  screening_results.csv
  summary.png
```

### `evaluate.py`

Evaluates generated 2D `.npy` designs against guideline criteria.

Default checks:

- minimum channel width >= `1.5 mm`
- mean wall thickness >= `0.5 mm`

Outputs:

- full metric table
- pass/fail summary figure
- copies or links of passing designs

### `generate_3d_volumes_finaloldver2.py`

Builds 3D scaffold volumes by interpolating through the VAE latent space.

The script is designed to generate:

- 70 pass volumes
- 30 fail volumes
- smooth 3D arrays, typically `384 x 384 x 384`

The method avoids direct 2D extrusion by decoding intermediate latent vectors into a stack of changing cross-sections.

### `evaluate_3d.py`

Evaluates 3D binary volumes and identifies best and worst candidate subsets.

Hard criteria include:

- wall thickness >= `0.50 mm`
- solid fraction >= threshold
- porosity >= threshold

Ranking score uses weighted geometric predictors:

- wall thickness
- solid fraction
- channel-width proxy

Outputs include:

- 3D metric table
- best subset
- worst subset
- statistical comparisons
- summary plot

### `merge_and_evaluate.py`

Combines two volume directories into one evaluation set and runs the same 3D ranking workflow.

This is useful when generated volumes are split across two runs or versions.

### `process.py`

Downsamples selected `.npy` volumes and removes floating disconnected components.

This prepares selected pass/fail examples for visualization or CAD conversion.

### `npy_to_step.py`

Converts selected processed `.npy` volumes into STEP geometry using CadQuery.

Main operations:

1. Loads selected pass/fail volumes.
2. Downsamples the volume.
3. Keeps the largest connected component.
4. Converts solid voxels into CAD boxes.
5. Exports a `.step` file for CAD/COMSOL import.

### `viewvolumes.py`

Uses PyVista to visualize a selected 3D `.npy` volume.

### `plot_channel_profile.py`

Plots the distribution of minimum channel widths across generated designs.

## Data and Output Files

| File/Folder | Meaning |
|---|---|
| `model_weights` | Pretrained VAE weights used for design generation. |
| `designs_metrics.csv` | Geometric metrics for generated 2D designs. |
| `evaluation_results.csv` | Evaluation output from screening. |
| `eval_3d_combined/` | Combined 3D evaluation outputs. |
| `eval_3d_combined/results.csv` | Full 3D metric and score table. |
| `eval_3d_combined/best_subset.csv` | Best-ranked candidate volumes. |
| `eval_3d_combined/worst_subset.csv` | Worst-ranked candidate volumes. |
| `eval_3d_combined/statistics.csv` | Statistical comparison between best and worst subsets. |
| `eval_3d_combined/comparison.png` | Visual summary of 3D evaluation results. |

## Requirements

Core:

```bash
pip install numpy scipy matplotlib scikit-image
```

For VAE generation:

```bash
pip install torch torchvision
```

For visualization:

```bash
pip install pyvista
```

For STEP export:

```bash
pip install cadquery
```

## Typical Usage

Generate and screen 2D designs:

```bash
python screen_and_generate.py --output_dir ./designs
```

Generate 3D volumes:

```bash
python generate_3d_volumes_finaloldver2.py
```

Evaluate 3D volumes:

```bash
python evaluate_3d.py --vol_dir ./volumes_3d --output_dir ./eval_3d
```

Merge two generated-volume sets:

```bash
python merge_and_evaluate.py --dir1 ./volumes_3d_v4 --dir2 ./volumes_3d_v4old --output_dir ./eval_3d_combined
```

View a selected volume:

```bash
python viewvolumes.py
```

Convert selected volumes to STEP:

```bash
python npy_to_step.py
```

## Notes

- Several scripts contain absolute paths from the original working machine. Update these before running on another computer.
- The pipeline assumes binary masks where one phase represents solid scaffold and the other represents void/channel space.
- EDT-based measurements are sensitive to image resolution and physical scale; keep `canvas_mm` consistent across generation and evaluation.
- Large 3D `.npy` volumes and STEP files can be very large and may be omitted from the repository.

