import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
import re
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

#paths for inputs and output 
PROCESSED = Path("data/processed/songs_mapped.csv")
OUT_MODEL = Path("models/new_song_mood_model.joblib")
OUT_MODEL.parent.mkdir(parents=True, exist_ok=True)

#configurations of the features and the target labels
FEATURE_WISHLIST = [
    "tempo","energy","valence","loudness",
    "danceability","speechiness","acousticness","instrumentalness","liveness"
]
TARGETS = ["happy","chill","sad","hyped"]
RANDOM_STATE = 42

#clean loudness column just in case, even though it will be dropped because it has NA
def clean_loudness(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()
    s = s.str.replace("\u2212", "-", regex=False)           
    s = s.str.replace(r"[dD][bB]", "", regex=True)          
    s = s.str.replace(r"[^0-9\.\-\+]", "", regex=True)      
    return pd.to_numeric(s, errors="coerce").clip(-60, 0)   

def normalize_features(df: pd.DataFrame) -> pd.DataFrame:
    #standardize common audio/ID columns to lowercase variants
    renamer = {
        "Tempo": "tempo",
        "Energy": "energy",
        "Positiveness": "valence",
        "Loudness (db)": "loudness_src",
        "Loudness (dB)": "loudness_src",
        "Danceability": "danceability",
        "Speechiness": "speechiness",
        "Liveness": "liveness",
        "Acousticness": "acousticness",
        "Instrumentalness": "instrumentalness",
        "Artist(s)": "artists",
        "song": "track_name",
    }
    present = {k: v for k, v in renamer.items() if k in df.columns}
    if present:
        df = df.rename(columns=present)

    # 2) build/repair 'loudness' from source columns if missing or all-NaN
    need_loudness = ("loudness" not in df.columns) or (df["loudness"].notna().sum() == 0)
    if need_loudness:
        src = None
        if "loudness_src" in df.columns and df["loudness_src"].notna().sum() > 0:
            src = df["loudness_src"]
        elif "Loudness (db)" in df.columns and df["Loudness (db)"].notna().sum() > 0:
            src = df["Loudness (db)"]
        elif "Loudness (dB)" in df.columns and df["Loudness (dB)"].notna().sum() > 0:
            src = df["Loudness (dB)"]
        if src is not None:
            df["loudness"] = clean_loudness(src)

    #dropping unused or obvious data leakage or uncorrelated columns
    leak_prefixes = ("Good for ", "Similar ", "Similarity Score")
    drop_cols = [c for c in df.columns if c == "Album" or any(c.startswith(p) for p in leak_prefixes)]
    if drop_cols:
        df = df.drop(columns=drop_cols, errors="ignore")

    return df

def diagnostics(df, feature_cols):
    print("\n=== DIAGNOSTICS ===")
    print(f"Rows: {len(df):,}")
    print("Columns:", list(df.columns))
    if "mood" in df.columns:
        print("\nLabel counts:")
        print(df["mood"].value_counts(dropna=False))
    print("\nFeature availability & non-null counts:")
    for c in feature_cols:
        nn = df[c].notna().sum() if c in df.columns else 0
        print(f"  {c:16s} exists={c in df.columns}  non-null={nn:,}")
    print("====================\n")

#training the model
def main():
    if not PROCESSED.exists():
        raise FileNotFoundError(f"Mapped file not found: {PROCESSED}. Run your map_labels.py first.")

    df = pd.read_csv(PROCESSED)
    df = normalize_features(df) #normalizing the data

    if "mood" not in df.columns:
        raise ValueError("Expected 'mood' column in mapped CSV.")

    #drop all the unused columns, keeping targets only
    df = df[df["mood"].isin(TARGETS)].copy()
    if df.empty:
        raise ValueError("After filtering to TARGETS, no rows remain. Check your mapping step.")

    # Figure out which desired features actually exist
    have = [c for c in FEATURE_WISHLIST if c in df.columns]
    if not have:
        raise ValueError(
            "None of the expected audio features are present. "
            f"Looked for: {FEATURE_WISHLIST}"
        )

    # Coerce numerics; imputer will handle remaining NaNs
    for c in have:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    diagnostics(df, have)

    X = df[have]
    y = df["mood"].astype(str)

    # If a column is entirely NaN, drop it
    all_nan_feats = [c for c in have if X[c].isna().all()]
    if all_nan_feats:
        print(f"WARNING: Dropping all-NaN features: {all_nan_feats}")
        X = X.drop(columns=all_nan_feats)
        have = [c for c in have if c not in all_nan_feats]
        if not have:
            raise ValueError("All candidate features were all-NaN after coercion.")

    #split the test into 80/20
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )

    #creating a pipeline for the model
    def make_pipe(est):
        return Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("clf", est),
        ])

    candidates = {
        "LogReg": make_pipe(LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE)),
        "KNN":    make_pipe(KNeighborsClassifier(n_neighbors=5)),
        "RF":     make_pipe(RandomForestClassifier(
                        n_estimators=400,
                        class_weight="balanced_subsample",
                        random_state=RANDOM_STATE
                    )),
    }

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    print("Model comparison (CV on train, then test on holdout):")
    best_name, best_pipe, best_cv = None, None, -1.0
    for name, pipe in candidates.items():
        cv_scores = cross_val_score(pipe, X_train, y_train, cv=skf)
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        test_acc = accuracy_score(y_test, y_pred)
        print(f"{name:6s}  CV={cv_scores.mean():.3f}±{cv_scores.std():.3f}  Test={test_acc:.3f}")
        if cv_scores.mean() > best_cv:
            best_cv, best_name, best_pipe = cv_scores.mean(), name, pipe

    # Final report
    y_pred = best_pipe.predict(X_test)
    labels_in_test = sorted(set(TARGETS) & set(y_test.unique()))
    print(f"\nBest model: {best_name}")
    print("\nClassification report:")
    print(classification_report(y_test, y_pred, labels=labels_in_test))

    cm = confusion_matrix(y_test, y_pred, labels=labels_in_test)
    print("\nConfusion matrix (rows=true, cols=pred):")
    print(pd.DataFrame(cm, index=labels_in_test, columns=labels_in_test))

    # Save pipeline (imputer+scaler+model)
    joblib.dump({
        "pipeline": best_pipe,
        "features": have,
        "labels": sorted(df["mood"].unique()),
        "version": "milestone1-new-song-1.2",
    }, OUT_MODEL)
    print(f"\nSaved model → {OUT_MODEL}")

    #trying out as a demo for a song - see what the model can output
    demo = pd.DataFrame([{
        "tempo": 120, "energy": 0.8, "valence": 0.7, "loudness": -5,
        "danceability": 0.6, "speechiness": 0.05, "acousticness": 0.1,
        "instrumentalness": 0.05, "liveness": 0.1
    }])
    demo = demo[[c for c in have if c in demo.columns]]  # align columns
    demo_pred = best_pipe.predict(demo)[0]
    demo_conf = float(np.max(best_pipe.predict_proba(demo)))
    print(f"\nDemo → mood={demo_pred}  confidence={demo_conf:.3f}")

if __name__ == "__main__":
    main()
