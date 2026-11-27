# DSF4E Challenge 1: Explorative Data Analysis

Analysis for the LaserCut GmbH case: the sales data is cleaned, linked to the DXF drawings of the parts, enriched with geometric and process features, and then visualised and checked for correlations with the estimated cutting time.

## Required packages

The code was run with Python 3.12.8. Install the packages from within this folder:

```bash
pip install -r requirements.txt
```

`requirements.txt` lists `pandas`, `matplotlib`, `ezdxf`, `shapely`, `jupyter` and `seaborn`. `numpy`, which `helpers.py` also imports, is installed as a dependency of these.

## How to run the code

All paths are relative, so the notebooks must be run with this folder as the working directory. Open each notebook in Jupyter or VS Code and choose **Run All**, in this order:

| Step | Notebook | Reads | Writes |
|---|---|---|---|
| 1 | `01_data_preparation.ipynb` | `data/customers_sales.csv`, file names in `10991360/` | `data/data_preparation_output.csv` |
| 2 | `02_analysis.ipynb` | `data/data_preparation_output.csv`, DXF files | `data/analysis_output_full.csv`, `data/analysis_output_parts.csv` |
| 3 | `03_plots.ipynb` | `data/analysis_output_full.csv` | plots (shown in the notebook) |
| 4 | `04_correlation.ipynb` | `data/analysis_output_full.csv` | correlation matrix and plots (shown in the notebook) |

Steps 3 and 4 only depend on the output of step 2.

Alternatively, run all four from the command line (this overwrites the stored cell outputs):

```bash
for nb in 0[1-4]_*.ipynb; do jupyter nbconvert --to notebook --execute --inplace "$nb"; done
```

## File contents

| File / folder | Content |
|---|---|
| `01_data_preparation.ipynb` | Corrects inconsistent customer names, adds parts without any sales, assigns customer IDs |
| `02_analysis.ipynb` | Computes the features per part (geometry, extraction method, cutting time) and exports the results |
| `03_plots.ipynb` | Plots the features and the extraction method against the estimated cutting time |
| `04_correlation.ipynb` | Pearson and Spearman correlations of the geometric features, one entry per part |
| `helpers.py` | Functions to read, measure and plot DXF files (bounding box, cutting length, holes, part area) |
| `requirements.txt` | Required Python packages |
| `10991360/` | 80 DXF drawings, `Geo (1).DXF` to `Geo (80).DXF` |
| `data/customers_sales.csv` | Input: customer, branch, file name and order quantity |
| `data/data_preparation_output.csv` | Cleaned sales data (output of step 1) |
| `data/analysis_output_full.csv` | Sales rows with all computed features (output of step 2) |
| `data/analysis_output_parts.csv` | One row per part with features, total sales and number of sales (output of step 2) |
| `getting_started.ipynb` | Introductory notebook of the challenge, not part of the pipeline |
| `Challenge 1_ Intro Slides.pdf` | Task description |

## Assumptions

**Data preparation**

- Duplicate rows in the sales data are treated as intentional and are kept.
- Parts that have a DXF file but no sales entry are added with an order quantity of 0.

**Cutting time**

Estimated cutting time = cutting length / cutting speed + 120 s general offset + extraction offset + 3 s per hole, with a cutting speed of 1000 mm/min. Only entities with the line type `Continuous` count as cut contours.

**Extraction method** (based on whether the bounding box fits the opening range, in either orientation)

| Method | Bounding box range (mm) | Extraction offset |
|---|---|---|
| Gate (SmartGate) | 30 × 30 to 160 × 160 | 2 s |
| Master (SortMaster) | 60 × 90 to 1500 × 2000 | 5 s |
| Gate + Master | fits both | 2 s (the faster one) |
| Manual | fits neither | 20 s |

The automation index is 0 for manual extraction and 1 otherwise.
