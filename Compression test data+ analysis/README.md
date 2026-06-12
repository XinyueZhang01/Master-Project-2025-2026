# Compression Test Data + Analysis

This folder contains Instron compression-test data and Python scripts used to process mechanical testing results for BNC, TPMS gyroid, and BNC-infilled gyroid scaffold samples.

The analysis converts raw force-displacement CSV files into engineering stress-strain curves, estimates Young's modulus from the initial loading region, exports processed curves, and generates publication-ready plots for comparing replicate samples.

## Contents

### Raw Instron CSV Files

Files such as:

- `BC333test1_1.csv`
- `BC666normaltest1_1.csv`
- `BC666thicktest1_1.csv`
- `NoBC4.5x3test1_1.csv`
- `pureBCtest1_1.csv`

represent compression-test exports from Instron testing. File naming generally encodes:

- `BC`: BNC-containing or BNC-grown sample
- `NoBC`: scaffold without BNC
- `Pure_TPMS` or `pureBC`: comparison material/sample group
- numeric labels such as `333`, `666`, `667`, `4.5x3`: gyroid cell-size or geometry variant
- `test1`, `test2`, `test3`: replicate number

### Processed Stress-Strain CSV Files

Files ending in:

```text
*_stress_strain_curve.csv
```

contain cleaned engineering strain and engineering stress values after baseline correction and unit conversion.

### Young's Modulus Summary Tables

Files ending in:

```text
*_youngs_modulus_results.csv
```

contain fitted Young's modulus values for replicate tests, typically with fit quality information such as `R^2`.

### Figures

Files ending in:

```text
*_three_stress_strain_curves.png
*_average_stress_strain_curve.png
```

show individual replicate stress-strain curves or averaged curves with standard-deviation bands.

## Scripts

### `plotstressstraincurve.py`

Processes three replicate Instron CSV files for one material or geometry group.

Main operations:

1. Reads Instron CSV files, skipping header rows.
2. Extracts time, displacement, and force columns.
3. Baseline-corrects displacement and force.
4. Converts force-displacement data into engineering stress-strain data.
5. Fits Young's modulus over a defined strain interval.
6. Plots replicate stress-strain curves.
7. Exports modulus results and processed curves.
8. Creates an averaged stress-strain curve with standard deviation.

Key user settings near the top of the script:

- input file names
- sample names
- material and structure labels
- sample width, depth, and height
- modulus fitting strain range
- plot axis limits

### `analysecompressiondata.py`

Performs higher-level mechanical interpretation using manually assembled modulus and geometry arrays.

Main operations:

1. Computes Pearson correlations between effective modulus and geometry parameters.
2. Fits a power-law relationship between modulus and solid fraction.
3. Estimates wall-thickness scaling using a cubic `t^3` relation.
4. Uses a Gibson-Ashby-style inversion to estimate required solid fraction for target moduli.

This script supports the design-guideline interpretation rather than raw Instron processing.

## Typical Usage

Edit the file list and sample dimensions in `plotstressstraincurve.py`, then run:

```bash
python plotstressstraincurve.py
```

Run the design-relationship analysis with:

```bash
python analysecompressiondata.py
```

## Requirements

```bash
pip install numpy pandas matplotlib scipy
```

## Outputs

The scripts generate:

- cleaned stress-strain CSVs
- Young's modulus result tables
- individual replicate stress-strain plots
- averaged stress-strain plots
- printed correlation and scaling relationships

## Notes

- Several output files are already included in this folder.
- `plotstressstraincurve.py` is configured for one sample group at a time; change the input filenames and dimensions before reusing it for another group.
- Stress is calculated from force divided by nominal cross-sectional area, so accurate sample dimensions are important.
- The fitting range should be checked for each material group to ensure it captures the initial linear region.

