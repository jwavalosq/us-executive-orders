#!/bin/bash
# Execute notebooks 00 to 06 in order, in place, with the eo-project kernel.
# Run from the project folder. Requires the .venv with ipykernel installed.
set -e
cd "$(dirname "$0")/.."
for nb in notebooks/00_setup_and_coverage.ipynb notebooks/01_the_complete_dataset.ipynb notebooks/02_descriptive_statistics.ipynb notebooks/03_categorization.ipynb notebooks/04_eras_and_history.ipynb notebooks/05_language_analysis.ipynb notebooks/06_search_the_archive.ipynb; do
  echo "Executing $nb"
  .venv/bin/python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=eo-project --ExecutePreprocessor.timeout=600 "$nb"
done
echo "All notebooks executed."
