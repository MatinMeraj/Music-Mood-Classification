# src/audio_viz.py
from pathlib import Path
import os
import pandas as pd
import sys
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

import joblib

# make sure Python can find audio_data.py
sys.path.append(os.path.dirname(__file__))
from audio_data import load_audio_data, TARGETS

FIG_DIR = Path("figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = Path("models/new_song_mood_model.joblib")

def plot_class_distribution(y):
    mood_counts = y.value_counts().reindex(TARGETS)
    plt.figure()
    plt.bar(mood_counts.index, mood_counts.values)
    plt.xlabel("Mood")
    plt.ylabel("Count")
    plt.title("Mood Class Distribution (Audio Dataset)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "mood_class_distribution.png")
    plt.close()

def plot_accuracy_bar(results):
    model_names = list(results.keys())
    cv_means = [results[m]["cv_mean"] for m in model_names]
    test_accs = [results[m]["test_acc"] for m in model_names]

    x = np.arange(len(model_names))
    width = 0.35

    plt.figure()
    plt.bar(x - width/2, cv_means, width, label="CV accuracy")
    plt.bar(x + width/2, test_accs, width, label="Test accuracy")
    plt.xticks(x, model_names)
    plt.ylabel("Accuracy")
    plt.title("Audio Model Accuracy (CV vs Test)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "audio_model_accuracy.png")
    plt.close()

def plot_rf_confusion_and_confidence(model, X_test, y_test):
    # RF (or best model) confusion matrix
    labels_in_test = sorted(set(TARGETS) & set(y_test.unique()))
    y_pred = model.predict(X_test)

    cm = confusion_matrix(y_test, y_pred, labels=labels_in_test)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels_in_test)
    disp.plot(values_format="d")
    plt.title("Confusion Matrix (Best Audio Model)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "best_model_confusion_matrix.png")
    plt.close()

    # confidence distribution
    proba = model.predict_proba(X_test)
    max_conf = proba.max(axis=1)

    plt.figure()
    plt.hist(max_conf, bins=20)
    plt.xlabel("Prediction confidence")
    plt.ylabel("Number of songs")
    plt.title("Best Model Prediction Confidence Distribution")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "best_model_confidence_distribution.png")
    plt.close()

def main():
    # load data and model
    X_train, X_test, y_train, y_test, feature_names = load_audio_data()
    bundle = joblib.load(MODEL_PATH)
    model = bundle["pipeline"]
    results = bundle["results"]

    # plots
    y_all = pd.concat([y_train, y_test])
    plot_class_distribution(y_all)

    plot_accuracy_bar(results)
    plot_rf_confusion_and_confidence(model, X_test, y_test)
    print(f"Saved figures in: {FIG_DIR}")

if __name__ == "__main__":
    main()
