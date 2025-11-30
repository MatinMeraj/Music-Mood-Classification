#!/usr/bin/env python
"""
Small demo for CMPT 310 Project
Audio mood prediction on 1–2 real songs from the dataset.

Usage:
    python src/demo.py
"""

import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

# Path to your trained audio model pipeline (.joblib)
AUDIO_MODEL_PATH = "models/new_song_mood_model.joblib"

# Turn this on if you later want to add manual lyrics + VADER again
USE_LYRICS = False

if USE_LYRICS:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Allow importing audio_data from the same folder
sys.path.append(os.path.dirname(__file__))
from audio_data import (
    TARGETS,
    FEATURE_WISHLIST,
    normalize_features,
    PROCESSED,
)

# Global variables populated at load time
FEATURE_NAMES_FOR_MODEL = None
LABEL_NAMES_FROM_JOBLIB = None


# ---------------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------------

def load_audio_model(path: str):
    """
    Load the audio model from joblib and pick up feature names + label names.

    Expected joblib structure (from train_audio_model.py):
      {
        "pipeline": best_pipe,
        "features": feature_names,
        "labels": sorted(y_train.unique()),
        "results": ...,
        "version": "milestone2-audio-1.0",
      }
    """
    global FEATURE_NAMES_FOR_MODEL, LABEL_NAMES_FROM_JOBLIB

    print(f"[INFO] Loading audio model from: {path}")
    obj = joblib.load(path)
    print(f"[INFO] Raw loaded object type: {type(obj)}")

    # Case 1: saved directly as a model/pipeline
    if hasattr(obj, "predict"):
        model = obj
        print("[INFO] Loaded object is a model with .predict().")
        FEATURE_NAMES_FOR_MODEL = (
            list(model.feature_names_in_) if hasattr(model, "feature_names_in_") else None
        )
        LABEL_NAMES_FROM_JOBLIB = None
        return model

    # Case 2: dict with pipeline, ...
    if isinstance(obj, dict):
        print(f"[INFO] Loaded a dict with keys: {list(obj.keys())}")

        # Label names
        if "labels" in obj:
            LABEL_NAMES_FROM_JOBLIB = list(obj["labels"])
            print(f"[INFO] labels from joblib: {LABEL_NAMES_FROM_JOBLIB}")
        else:
            LABEL_NAMES_FROM_JOBLIB = None
            print("[WARN] No 'labels' found; will fall back to model.classes_.")

        # Get the pipeline
        model = obj.get("pipeline", None)
        if model is None or not hasattr(model, "predict"):
            model = None
            for key, val in obj.items():
                if hasattr(val, "predict"):
                    model = val
                    print(f"[INFO] Found model inside dict at key: '{key}'")
                    break

        if model is None:
            raise TypeError(
                "Loaded dict does not contain a usable model with .predict(). "
                f"Available keys: {list(obj.keys())}"
            )

        # Feature names used during training
        if hasattr(model, "feature_names_in_"):
            FEATURE_NAMES_FOR_MODEL = list(model.feature_names_in_)
            print(f"[INFO] feature_names_in_ from model: {FEATURE_NAMES_FOR_MODEL}\n")
        else:
            FEATURE_NAMES_FOR_MODEL = obj.get("features", None)
            print(f"[WARN] Model has no feature_names_in_; using joblib['features']: {FEATURE_NAMES_FOR_MODEL}\n")

        return model

    raise TypeError(
        f"Unexpected object type loaded from {path}: {type(obj)}. "
        "Expected a sklearn estimator or a dict containing one."
    )


# LOAD DATASET FOR DEMO


def load_full_dataset_for_demo():
    """
    Load the full processed CSV, normalize it in the same way as during training,
    and build the feature matrix X and metadata (title, artist, true mood).
    """
    if not PROCESSED.exists():
        raise FileNotFoundError(f"Processed CSV not found: {PROCESSED}")

    print(f"[INFO] Loading dataset from: {PROCESSED}")
    df = pd.read_csv(PROCESSED)
    df = normalize_features(df)

    if "mood" not in df.columns:
        raise ValueError("Expected 'mood' column in mapped CSV.")

    # Keep only target moods
    df = df[df["mood"].isin(TARGETS)].copy()
    if df.empty:
        raise ValueError("No rows remain after filtering to TARGETS. Check your mapping step.")

    if "track_name" in df.columns and "artists" in df.columns:
        df = df.drop_duplicates(subset=["track_name", "artists", "mood"], keep="first")
        
    # Figure out which feature columns to use (must match training)
    if FEATURE_NAMES_FOR_MODEL is not None:
        feat_cols = FEATURE_NAMES_FOR_MODEL
    else:
        feat_cols = [c for c in FEATURE_WISHLIST if c in df.columns]

    if not feat_cols:
        raise ValueError(
            "No overlapping feature columns between model and CSV. "
            f"Model expects: {FEATURE_NAMES_FOR_MODEL}, CSV has: {df.columns.tolist()}"
        )

    # Coerce feature columns numeric
    for c in feat_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    X = df[feat_cols]

    # Build metadata
    # and normalize_features already renamed 
    title_col = "track_name" if "track_name" in df.columns else None
    artist_col = "artists" if "artists" in df.columns else None

    meta = pd.DataFrame(index=df.index)
    meta["true_mood"] = df["mood"].astype(str)
    if title_col:
        meta["title"] = df[title_col].astype(str)
    else:
        meta["title"] = [f"Song_{i}" for i in range(len(df))]
    if artist_col:
        meta["artist"] = df[artist_col].astype(str)
    else:
        meta["artist"] = "Unknown Artist"

    return X, meta


# PREDICTION HELPERS


def get_label_names(model, num_classes: int):
    """
    Determine the label names in the correct order, matching predict_proba output.
    """
    # Prefer labels from joblib if they exist and match the size
    if LABEL_NAMES_FROM_JOBLIB is not None and len(LABEL_NAMES_FROM_JOBLIB) == num_classes:
        return LABEL_NAMES_FROM_JOBLIB

    # Fallback
    if hasattr(model, "classes_") and len(model.classes_) == num_classes:
        return list(model.classes_)

    # Last resort: generic names
    print("[WARN] Could not match label names exactly; using generic names.")
    return [f"class_{i}" for i in range(num_classes)]


def select_high_confidence_indices(model, X, top_k: int = 2):
    """
    Run model.predict_proba on all rows in X and return the indices of the
    top-k most confident predictions (highest max probability).
    """
    if not hasattr(model, "predict_proba"):
        raise AttributeError("Model does not support predict_proba; cannot select by confidence.")

    probs = model.predict_proba(X)  # shape: (N, C)
    max_probs = probs.max(axis=1)   

    # Sort by confidence, descending
    order = np.argsort(-max_probs)
    top_indices = order[:top_k]

    return top_indices, probs


def print_demo_result(idx, X, meta, model, probs, label_names):
    """
    Print a pretty summary for a single song (row index idx).
    """
    row_features = X.iloc[idx]
    row_meta = meta.iloc[idx]
    prob_vec = probs[idx]

    true_mood = row_meta["true_mood"]
    title = row_meta["title"]
    artist = row_meta["artist"]

    pred_idx = prob_vec.argmax()
    pred_mood = label_names[pred_idx]
    confidence = float(prob_vec[pred_idx])

    print("=" * 70)
    print(f"Song: {title}  |  Artist: {artist}")
    print(f"Dataset true mood: {true_mood}")
    print("-" * 70)

    print("Audio model prediction:")
    print(f"  → Predicted mood: {pred_mood}  (confidence = {confidence:.3f})")
    print("  Probabilities:")
    for mood_label, p in zip(label_names, prob_vec):
        print(f"    {mood_label:>6}: {p:.3f}")

    agreement = "AGREE ✅" if pred_mood == true_mood else "DISAGREE ⚠️"
    print(f"\nOverall: model vs dataset label → {agreement}")
    print("=" * 70 + "\n")



def map_compound_to_mood(compound: float) -> str:
    """
    Simple heuristic to map VADER compound score to 4 moods.
    Only used if you enable USE_LYRICS and manually supply lyrics.
    """
    if compound <= -0.3:
        return "sad"
    elif compound < 0.1:
        return "chill"
    elif compound < 0.6:
        return "happy"
    else:
        return "hyped"


def predict_lyrics_mood(analyzer, lyrics: str):
    scores = analyzer.polarity_scores(lyrics)
    compound = scores["compound"]
    mood = map_compound_to_mood(compound)
    return mood, compound, scores


# MAIN

def main():
    # 1) Load trained model
    model = load_audio_model(AUDIO_MODEL_PATH)

    # 2) Load full dataset (same CSV as training) for demo
    X, meta = load_full_dataset_for_demo()
    print(f"[INFO] Loaded {len(X)} songs for demo search.\n")

    # 3) Select top-2 highest-confidence songs
    top_indices, probs = select_high_confidence_indices(model, X, top_k=2)
    num_classes = probs.shape[1]
    label_names = get_label_names(model, num_classes)

    print("[INFO] Running demo on top-2 highest-confidence songs...\n")

    # 4) Print results for each selected song
    for idx in top_indices:
        print_demo_result(idx, X, meta, model, probs, label_names)


if __name__ == "__main__":
    main()
