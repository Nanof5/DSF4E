"""Führt alle Notebooks der Challenge nacheinander aus: python3 run_all.py"""

from pathlib import Path

import nbformat
from nbclient import NotebookClient

ordner = Path(__file__).resolve().parent
notebooks = [
    "01_data_preparation.ipynb",
    "02_analysis.ipynb",
    "03_plots.ipynb",
    "04_correlation.ipynb",
]

for name in notebooks:
    print(f"Starte {name} ...")
    nb = nbformat.read(ordner / name, as_version=4)
    NotebookClient(
        nb,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": str(ordner)}},
    ).execute()
    nbformat.write(nb, ordner / name)

print("Alle Notebooks erfolgreich ausgeführt.")
