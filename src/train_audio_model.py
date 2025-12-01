# src/train_audio_model.py
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
import os
import sys
import numpy as np
import joblib

from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

#make sure Python can find audio_data.py in the same folder
sys.path.append(os.path.dirname(__file__))
from audio_data import load_audio_data, TARGETS  

OUT_MODEL = Path("models/new_song_mood_model.joblib")
OUT_MODEL.parent.mkdir(parents=True, exist_ok=True)


def make_pipe(est):
        
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", est),
    ])


def main():
    #taking the data from audio_data.py
    X_train, X_cv, X_test, y_train, y_cv, y_test, feature_names = load_audio_data()

    print("Train shape:", X_train.shape)
    print("Test shape:", X_test.shape)
    print("Features:", feature_names)
    print("Targets :", TARGETS)

    candidates = {
        "LogReg": make_pipe(LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        )),
        "KNN": make_pipe(KNeighborsClassifier(n_neighbors=5)),
        "RF": make_pipe(RandomForestClassifier(
            n_estimators=400,
            class_weight="balanced_subsample",
            random_state=42
        )),
    }

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = {}
    best_name, best_pipe, best_cv = None, None, -1.0

    print("\nModel comparison (5-fold CV on train, then test on holdout):")
    for name, pipe in candidates.items():
        cv_scores = cross_val_score(pipe, X_train, y_train, cv=skf)
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        test_acc = accuracy_score(y_test, y_pred)

        print(f"{name:6s}  CV={cv_scores.mean():.3f}±{cv_scores.std():.3f}  Test={test_acc:.3f}")

        results[name] = {
            "cv_mean": float(cv_scores.mean()),
            "cv_std": float(cv_scores.std()),
            "test_acc": float(test_acc),
        }

        if cv_scores.mean() > best_cv:
            best_cv, best_name, best_pipe = cv_scores.mean(), name, pipe

    #report best model
    y_pred = best_pipe.predict(X_test)
    labels_in_test = sorted(set(TARGETS) & set(y_test.unique()))
    print(f"\nBest model: {best_name}")
    print("\nClassification report:")
    print(classification_report(y_test, y_pred, labels=labels_in_test))

    cm = confusion_matrix(y_test, y_pred, labels=labels_in_test)
    print("\nConfusion matrix (rows=true, cols=pred):")
    print(labels_in_test)
    print(cm)

    #saving the best model to joblib so we don't have to 
    joblib.dump({
        "pipeline": best_pipe,
        "features": feature_names,
        "labels": sorted(y_train.unique()),
        "results": results,
        "version": "milestone2-audio-1.0",
    }, OUT_MODEL)
    print(f"\nSaved model → {OUT_MODEL}")


if __name__ == "__main__":
    main()
