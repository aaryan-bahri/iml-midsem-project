# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Ashoka CS-3410 / MAT-3211-1 midterm, Track C (Weather and Climate), Kaggle competition `iml-2026-track-c-extreme-rainfall`. Predict the probability that tomorrow's rain is >= 64.5 mm at a station from today's weather. Data are **simulated**. Primary metric: average precision. Classical ML only (no neural nets/pretrained models); trees/boosting are allowed if explainable in the viva.

Reference docs in the repo root: [IML_Midterm_Project_Guide.pdf](IML_Midterm_Project_Guide.pdf) (Track C is section 5; minimum experimental standard is section 6.2), [IML_Midterm_Student_Handout.pdf](IML_Midterm_Student_Handout.pdf), [track_c_starter.ipynb](track_c_starter.ipynb) (protocol only, not a good model), [rules.md](rules.md). The user has been granted a deadline extension; do not raise the original 30 Oct deadline.

## Commands

Python 3.13 venv at `.venv` (the default `python` on this machine is an MSYS2 build with no wheels; use `.venv\Scripts\python.exe`). Pinned in [requirements.txt](requirements.txt).

Rebuild everything (about 3 min), writing `submission.csv` and `experimental_results.csv` in the repo root:

```
.venv\Scripts\python.exe -c "import nbformat, nbclient; nb=nbformat.read('rainfall.ipynb',4); nbclient.NotebookClient(nb, timeout=1800, kernel_name='python3').execute(); nbformat.write(nb,'rainfall.ipynb')"
```

Use the venv's nbclient, not a bare `jupyter` command: `jupyter` on PATH resolves to Anaconda, whose kernel lacks lightgbm.

## Architecture

All code is in [rainfall.ipynb](rainfall.ipynb); edit the notebook directly (no generator script). Data lives in `iml-2026-track-c-extreme-rainfall/` (the zip is a duplicate).

Structure of the notebook, which encodes the validation protocol:
- **Feature groups** (`build_features` returns `{group: DataFrame}`): static, weather, calendar, physical, history, anomaly, missing, station. Every experiment changes exactly one group via `fm(groups, G)`. All features are backward-looking per station; a perturb-the-future test in section 2 asserts no look-ahead.
- **Folds:** `DEV` = tuning folds (validate 2015-2018, train on earlier years, 4 stations held out per fold). `HOLD` = 2019-2020 holdout, scored once in section 7 after all choices are frozen. `test.csv` is read only in section 9.
- **Harness:** `run(fit_pred, folds)` -> per-fold AP on seen/unseen stations; `sk()` and `lgbm()` build fit-predict closures; `compare()` applies the adoption rule (better in >= 3 of 4 folds and on average). Experiments E1-E5 and model selection feed forward programmatically (`FS`, `DECAY`, `CW`, `C_BEST`, `LG_BEST`, `W`), so rerunning the notebook re-derives the configuration.
- Final model: probability blend of tuned logistic regression and LightGBM, refit on all of 2010-2020.

## Constraints

- `rain_tomorrow_mm` (train only) defines the label: never a feature. The next row's `rain_today_mm` equals this row's `rain_tomorrow_mm`, so lags must only look backward.
- Test has 4 stations unseen in training and covers 2021-2024; the climate drifts, so validate chronologically and by station. Never use random splits for model selection.
- Do not use the test file's features to make modelling decisions.
- The README must declare Claude Code usage (course generative-AI policy). `experimental_results.csv` columns were chosen by us; the course template was not provided, so conform them when it is.
