"""Run every cell of rainfall.ipynb from top to bottom.

Usage (from the project folder, with the project's virtual environment):
    python run_all.py

It rewrites submission.csv and experimental_results.csv in the folder where it is started.
"""
import nbformat
import nbclient

# Read the notebook file.
notebook = nbformat.read("rainfall.ipynb", 4)

# Run all cells in a fresh Python kernel.
# The timeout is long on purpose: the whole notebook takes about 13 minutes.
client = nbclient.NotebookClient(notebook, timeout=1800, kernel_name="python3")
client.execute()

# Save the notebook again so that it contains the fresh outputs.
nbformat.write(notebook, "rainfall.ipynb")
print("done: submission.csv and experimental_results.csv were rewritten")
