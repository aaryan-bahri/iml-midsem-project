# Aaryan Bahri — IML Midterm Project, Track C

> Individual submission for CS-3410 / MAT-3211-1, Ashoka University.
> The dataset is **simulated**; see the track's Kaggle page.

| Field | Value |
|---|---|
| Student | Aaryan Bahri, 1020241435|
| Kaggle username | aaryanbahri |
| Track | C Weather and Climate |
| Team (leaderboard only) | ANA |
| Research question | When validation mimics the test set (later years, unseen stations), how much lower is average precision than under a random split, and which design choices help under that shift? |

**AI disclosure:** Claude Code (Anthropic) was used for coding help and for building this README and generating latex code for the report.

## 1. Environment
- Python 3.13 (developed on 3.13.1); operating system Windows 11.
- Install (from the project folder):
  ```bash
  python -m venv .venv
  .venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
  pip install -r requirements.txt   # every version pinned
  ```
- Hardware used: Intel Core i7-13700H, 32 GB RAM. Runtime: about 13 minutes for the whole notebook (LightGBM runs on one thread so that results are deterministic).

## 2. Data
Download `train.csv`, `test.csv` and `sample_submission.csv` from the course dataset
(https://www.kaggle.com/datasets/samarjeetsinghmalik/iml2026-track-c-simulated-extreme-rain, competition `iml-2026-track-c-extreme-rainfall`)
into `iml-2026-track-c-extreme-rainfall/` (as in this repository). The notebook also finds the data in `data/`, in `/kaggle/input/...`, or in the folder named by the environment variable `IML_DATA_DIR`.

## 3. Reproduce everything
```bash
python run_all.py
```
This runs every cell of `rainfall.ipynb` from top to bottom and regenerates every table, `experimental_results.csv` (44 runs) and `submission.csv` (both written in the project folder, not in `predictions/`).
Run it with the virtual environment's Python (`.venv\Scripts\python.exe run_all.py` on Windows). A repeated run gave a byte-identical `submission.csv`.

## 4. Map from report to code
All code is in `rainfall.ipynb`; sections are the notebook's headings.

| Report item | Produced by |
|---|---|
| Table 1 (baselines, tuned models, final blend) | Section 4 (baselines, dev), Section 6 (tuned models and blend, dev), Section 7 (holdout table) |
| Table 2 (E1 validation scheme) | Section 5, cell E1 |
| Table 3 (experiments E2–E6) | Section 5, cells E2 to E6 |
| Operating-point numbers (in the text) | Section 8, first cell |
| Figure 1 (data audit) | Section 1 plot |
| Figure 2 (reliability and precision–recall) | Section 8 plot |
| Table 4, appendix (feature groups) | Section 2, `build_features` |
| Table 5, appendix (model selection) | Section 6 |
| Error analysis (season, station, caught vs missed) | Section 8, second cell |
| Prediction file `submission.csv` | Section 9 |
| `experimental_results.csv` | last code cell of the notebook |

The two PNGs in `report/figures/` are copies of the plots the notebook displays (Section 1 and Section 8); the notebook does not save them itself.

## 5. Seeds and determinism
- `SEED = 42` in Section 0 sets the NumPy seed; the same seed fixes the station blocks of the folds (`RandomState(42)`), the random folds in E1 and the bootstrap.
- LightGBM uses seed 42 during tuning and seeds 42–46 (averaged) for the holdout and the final model, with `deterministic=True` and one thread.
- No remaining non-determinism was observed on this machine. Other library versions or hardware may change the last digits, which is why versions are pinned.

## 6. Methods used
Models, with where they come from (the project guide, Table 3):
- **Taught in lectures:** logistic regression (the reference model and the main model), linear discriminant analysis, Gaussian Naive Bayes, linear SVM; plus a constant (prior) baseline and a climatology baseline.
- **Classical, not yet taught:** LightGBM, gradient-boosted decision trees (Ke et al., 2017), used as an additional model and blended with logistic regression.
- No neural networks, deep learning, or pretrained or foundation models.

What each step does, why we did it, and what it changed in the model (dev = four chronological tuning folds, score = mean AP on seen and held-out stations):

| Step | Why | Result and effect on the final model |
|---|---|---|
| Data audit (Section 1) | Find the data's traps before modelling | 3.3% positives; frequency rises from 2.6% (2010) to 4.2% (2020); 63% of positives in June–September; outages in 4 columns. This led to AP as the metric, chronological folds, held-out stations and outage flags. |
| Leakage guard (Section 2) | Make sure no feature uses tomorrow's information | `rain_tomorrow_mm` is never a feature (the next row's `rain_today_mm` equals it in 100% of rows). A test that perturbs the future and checks earlier features passes, so validation scores are trustworthy. |
| Feature groups (Section 2) | Let each experiment change exactly one thing | 11 named groups (8 plus 3 spatial) built from today and earlier days only. |
| Validation folds (Section 3) | Mimic the test set: later years and unseen stations | 4 tuning folds (2015–2018) with 4 stations held out each, and a 2019–2020 holdout scored once, so tuning does not inflate the final number. |
| Baselines (Section 4) | Give the model something to beat | Constant 0.036, climatology 0.081, default logistic regression 0.215 (the reference), LDA 0.198, Gaussian NB 0.159, linear SVM 0.207. |
| E1 validation scheme | Measure how much a random split flatters the model | Random beats chronological by only 0.009 (LR) and 0.015 (LightGBM), below the fold spread of about 0.04; held-out stations were not harder. No change to the model. |
| E2 feature groups | Find which information helps | Calendar, history, anomaly and outage flags adopted (0.2145 → 0.2263); the physical group is not (a linear model can form those differences itself). |
| E3 station identity | Check transfer to unseen stations | Station facts kept (dropping them cost 0.005); station one-hot not used. |
| E4 recency weights | Test whether older years should count less under drift | Did not help; all years weigh the same. |
| E5 class weights | Test a common fix for rare events | Did not help (AP uses ranks); natural class balance kept. |
| E6 spatial features | Use other stations' same-day readings (disturbances travel) | Only the same-day mean of all other stations (`regional`) adopted: LightGBM +0.0076, logistic regression +0.0011. Upwind never helped. |
| Tuning (Section 6) | Choose settings without touching the holdout | Logistic regression C = 0.1; LightGBM 15 leaves, 300 rows per leaf, 400 trees; 50/50 blend. Dev score 0.2336 (blend) vs 0.2292 (LR) and 0.2306 (LightGBM). |
| Holdout (Section 7) | Honest final estimate with uncertainty | AP 0.149 (95% interval 0.124–0.179; base rate 0.042); +0.011 over the default logistic regression (interval +0.003 to +0.019); not distinguishable from tuned logistic regression. |
| Error analysis and calibration (Section 8) | See where the model fails and whether probabilities are reliable | Better in the monsoon (0.183 vs 0.100); misses 77% of events at the chosen threshold because most heavy-rain days show no strong signal today; probabilities about 12% too low (drift); AP is unaffected by calibration. |
| Final fit and submission (Section 9) | Use all labelled data to predict the test set | Refit on 2010–2020, predict once, check the file format, write `submission.csv`. The public leaderboard score of this model is 0.1729 (30% of test rows). |

## 7. Sources and adapted code
- **Dataset:** IML 2026 Track C simulated extreme rain (course dataset on Kaggle, files dated 15 October 2026).
- **Course material:** project guide and handout; the course starter notebook `track_c_starter.ipynb`. The data-folder lookup in Section 0 of the notebook is adapted from the starter; the rest of the code is our own.
- **Libraries:** pandas 3.1.0, NumPy 2.5.4, scikit-learn 1.9.1 (Pedregosa et al., 2011), LightGBM 4.7.0 (Ke et al., 2017), matplotlib 3.11.2, nbformat and nbclient (to run the notebook).
- **Papers:** none were used beyond the two library papers above; the report's reference list contains only the dataset, the two libraries and the starter notebook.

## 8. Declaration
I confirm that this submission is my own individual work and that I can explain every part of it.
