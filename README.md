# Project 72 — Network intrusion detection (UNSW-NB15)

This is a small, practical Python project for **Project 72**: train a classifier on the **UNSW-NB15** dataset and see how well it tells **normal traffic** from **attacks**. You do not need to be a security expert to run it; the script does the heavy lifting and writes a few files you can open afterward.

---

## What you get

The script trains a **Random Forest** (100 trees) on the official train split and evaluates on the held-out test split. You will see a classification report in the terminal and saved files under **`results/`**: a confusion matrix plot, feature importances (chart + spreadsheet), plain-text metrics, and a pickled model if you want to load it later in Python.

Rough ballpark on a typical laptop: a short wait while the forest trains, then you are done.

---

## About the dataset

**UNSW-NB15** comes from UNSW (Australian Centre for Cyber Security). It is a common benchmark for intrusion detection with **binary labels**: `0` = normal, `1` = attack. The project originally referenced older benchmarks like NSL-KDD; UNSW-NB15 is newer and closer to how people talk about “modern” attack mixes today.

If you are curious about scale: on the usual split there are on the order of **80k+ training rows** and **170k+ test rows**, with dozens of numeric and categorical flow features after preprocessing.

---

## How it works (in plain language)

1. **Data** — The script looks for two CSV files in `data/`. If they are not there, it **downloads a ready-made zip from GitHub** (same filenames as the common Kaggle layout) and unpacks them. You can also drop the files in yourself if you prefer (for example from [Kaggle](https://www.kaggle.com/datasets/mrwellsdavid/unsw-nb15)).

2. **Preprocessing** — It drops columns that are not inputs (`id`, and `attack_cat` when present), turns categories like `proto`, `service`, and `state` into numeric columns, and lines up train and test so column names match.

3. **Model** — A Random Forest learns patterns that separate normal from attack traffic.

4. **Outputs** — Metrics and plots land in `results/` so you can drop them into a report or slide deck without re-running anything.

---

## Run it

From the folder that contains `main.py`:

```bash
pip install -r requirements.txt
python main.py
```

First run with an empty `data/` folder: the script will fetch the dataset for you. After that, it reuses the CSVs unless you delete them.

---

## What ends up in `results/`

| File | What it is |
|------|------------|
| `metrics.txt` | Classification report plus ROC-AUC (same idea as what prints in the console) |
| `confusion_matrix.png` | Quick visual of where the model gets confused |
| `feature_importance.csv` | Full ranked list of feature importances from the forest |
| `feature_importance.png` | Bar chart of the top features (easy to skim) |
| `model.pkl` | The trained model; load with `pickle` in Python if you extend the project |

---

## Stack

Python 3.x, **pandas**, **scikit-learn** (Random Forest), **matplotlib** (plots). **NumPy** is listed in `requirements.txt` because other libraries expect it; you do not have to import it yourself in this script.

---

## Further reading

- Moustafa & Slay (2015). *UNSW-NB15: A Comprehensive Dataset*. IEEE MilCIS — the dataset paper.
- If you later add richer explanations, Lundberg & Lee (2017) on **SHAP** is the usual starting point for “why did the model say that?”

---

If something fails (network block, missing permissions), put **UNSW_NB15_training-set.csv** and **UNSW_NB15_testing-set.csv** manually into the **`data/`** folder next to `main.py` and run again. That path is the most reliable offline option.
