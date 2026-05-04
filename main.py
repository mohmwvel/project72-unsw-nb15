import os
import sys
import pickle
import zipfile
import urllib.request
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_CSV = os.path.join("data", "UNSW_NB15_training-set.csv")
TEST_CSV = os.path.join("data", "UNSW_NB15_testing-set.csv")
RESULTS = "results"
ZIP_URL = "https://github.com/InitRoot/UNSW_NB15/raw/master/UNSW_NB15.zip"


def ensure_directories():
    os.makedirs("data", exist_ok=True)
    os.makedirs(RESULTS, exist_ok=True)


def ensure_dataset():
    if os.path.isfile(TRAIN_CSV) and os.path.isfile(TEST_CSV):
        return

    print("Downloading UNSW-NB15 from a public mirror...")
    tmp = os.path.join("data", "_nb15.zip")
    try:
        urllib.request.urlretrieve(ZIP_URL, tmp)
        with zipfile.ZipFile(tmp, "r") as zf:
            zf.extractall("data")
    except Exception as e:
        print("Download failed:", e)
        print("Add the two CSV files to:", os.path.join(BASE_DIR, "data"))
        sys.exit(1)
    finally:
        if os.path.isfile(tmp):
            os.remove(tmp)


def load_data():
    train = pd.read_csv(TRAIN_CSV)
    test = pd.read_csv(TEST_CSV)

    drop = [c for c in ("id", "attack_cat") if c in train.columns]
    X_train = train.drop(columns=drop + ["label"])
    y_train = train["label"]

    drop_t = [c for c in ("id", "attack_cat") if c in test.columns]
    X_test = test.drop(columns=drop_t + ["label"])
    y_test = test["label"]

    return X_train, X_test, y_train, y_test


def preprocess(X_train, X_test):
    cats = [c for c in ("proto", "service", "state") if c in X_train.columns]
    X_train = pd.get_dummies(X_train, columns=cats)

    X_test = pd.get_dummies(
        X_test,
        columns=[c for c in ("proto", "service", "state") if c in X_test.columns],
    )

    X_train, X_test = X_train.align(X_test, join="left", axis=1, fill_value=0)
    return X_train, X_test


def fit_model(X_train, y_train):
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    return model


def evaluate(model, X_test, y_test):
    y_pred = model.predict(X_test)
    proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, proba)
    report = classification_report(y_test, y_pred, target_names=["Normal", "Attack"])
    cm = confusion_matrix(y_test, y_pred)
    return report, auc, cm


def save_results(report, auc, cm, imp, model):
    with open(os.path.join(RESULTS, "metrics.txt"), "w") as f:
        f.write(report + f"\nROC-AUC: {auc:.4f}\n")

    imp.to_csv(os.path.join(RESULTS, "feature_importance.csv"))

    with open(os.path.join(RESULTS, "model.pkl"), "wb") as f:
        pickle.dump(model, f)


def plot_confusion_matrix(cm):
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["Normal", "Attack"])
    ax.set_yticklabels(["Normal", "Attack"])
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion matrix")

    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=12)

    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "confusion_matrix.png"), dpi=120)
    plt.close(fig)


def plot_feature_importance(imp):
    top = imp.head(12)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.barh(top.index[::-1], top.values[::-1])
    ax.set_xlabel("Importance")
    ax.set_title("Top features")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "feature_importance.png"), dpi=120)
    plt.close(fig)


def main():
    os.chdir(BASE_DIR)
    ensure_directories()
    ensure_dataset()

    X_train, X_test, y_train, y_test = load_data()
    X_train, X_test = preprocess(X_train, X_test)

    print(f"Train {len(y_train)} rows | Test {len(y_test)} rows | {X_train.shape[1]} features")

    model = fit_model(X_train, y_train)
    report, auc, cm = evaluate(model, X_test, y_test)

    print(report)
    print(f"ROC-AUC: {auc:.4f}")

    imp = pd.Series(model.feature_importances_, index=X_train.columns).sort_values(ascending=False)
    save_results(report, auc, cm, imp, model)
    plot_confusion_matrix(cm)
    plot_feature_importance(imp)

    print(f"Saved outputs under {RESULTS}/")


if __name__ == "__main__":
    main()
