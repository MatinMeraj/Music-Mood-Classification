#!/usr/bin/env python
"""
Small demo for CMPT 310 Project
Audio (+ optional lyrics) mood prediction on 1–2 demo songs.

Usage:
    python src/demo.py
"""

import math
import joblib
import pandas as pd

# Set this to False if you DON'T want to demo lyrics
USE_LYRICS = True

if USE_LYRICS:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

# Path to your trained audio model pipeline (.joblib)
AUDIO_MODEL_PATH = "models/new_song_mood_model.joblib"

# Fallback label order (only used if we can't recover true label names)
MOOD_LABELS = ["happy", "chill", "sad", "hyped"]

# Base audio features we manually provide per demo song
BASE_AUDIO_KEYS = [
    "tempo",
    "energy",
    "valence",
    "danceability",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "loudness",  # OK to have extra; we won't pass it if model doesn't use it
]

# Will be filled dynamically after loading the model
FEATURE_NAMES_FOR_MODEL = None
LABEL_NAMES_FROM_JOBLIB = None


# ---------------------------------------------------------
# DEMO SONGS
# (You can replace these with real rows from your dataset)
# ---------------------------------------------------------

DEMO_SONGS = [
    {
        "id": "demo_song_1",
        "title": "Bright Morning",
        "audio_features": {
            "tempo": 124.0,
            "energy": 0.78,
            "valence": 0.82,
            "loudness": -5.2,
            "danceability": 0.73,
            "speechiness": 0.05,
            "acousticness": 0.12,
            "instrumentalness": 0.0,
            "liveness": 0.15,
        },
        "lyrics": """
        Woke up to the sunlight on my face,
        Every little worry slowly fades away,
        Holding on to this feeling, I’m alive,
        Nothing’s gonna break my stride tonight.
        """,
    },
    {
        "id": "demo_song_2",
        "title": "Midnight City Rain",
        "audio_features": {
            "tempo": 95.0,
            "energy": 0.38,
            "valence": 0.25,
            "loudness": -9.5,
            "danceability": 0.48,
            "speechiness": 0.04,
            "acousticness": 0.42,
            "instrumentalness": 0.0,
            "liveness": 0.11,
        },
        "lyrics": """
        Streetlights flicker on the empty road,
        Echoes of a memory I used to know,
        Walking through the city in the pouring rain,
        Every step is heavy with a quiet pain.
        """,
    },
]


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def load_audio_model(path: str):
    """
    Load the audio model from joblib and pick up feature names + label names.
    """
    global FEATURE_NAMES_FOR_MODEL, LABEL_NAMES_FROM_JOBLIB

    print(f"[INFO] Loading audio model from: {path}")
    obj = joblib.load(path)
    print(f"[INFO] Raw loaded object type: {type(obj)}")

    # Case 1: direct model
    if hasattr(obj, "predict"):
        model = obj
        print("[INFO] Loaded object is a model with .predict().")
        FEATURE_NAMES_FOR_MODEL = (
            list(model.feature_names_in_) if hasattr(model, "feature_names_in_") else None
        )
        LABEL_NAMES_FROM_JOBLIB = None
        return model

    # Case 2: dict with model + metadata
    if isinstance(obj, dict):
        print(f"[INFO] Loaded a dict with keys: {list(obj.keys())}")

        # Label names from label encoder
        if "label_encoder_classes" in obj:
            LABEL_NAMES_FROM_JOBLIB = list(obj["label_encoder_classes"])
            print(f"[INFO] label_encoder_classes: {LABEL_NAMES_FROM_JOBLIB}")
        else:
            LABEL_NAMES_FROM_JOBLIB = None
            print("[WARN] No label_encoder_classes found; will fall back to model.classes_.")

        # Find actual model
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

        # Feature names from training, if available
        if hasattr(model, "feature_names_in_"):
            FEATURE_NAMES_FOR_MODEL = list(model.feature_names_in_)
            print(f"[INFO] feature_names_in_ from model: {FEATURE_NAMES_FOR_MODEL}\n")
        else:
            FEATURE_NAMES_FOR_MODEL = None
            print("[WARN] Model has no feature_names_in_; will fall back to base keys.\n")

        return model

    # Anything else:
    raise TypeError(
        f"Unexpected object type loaded from {path}: {type(obj)}. "
        "Expected a sklearn estimator or a dict containing one."
    )


def build_feature_row_for_model(base_features: dict) -> dict:
    """
    Given base raw features (tempo, energy, valence, danceability, etc.),
    build a single-row feature dict that matches exactly the feature names
    used during training (FEATURE_NAMES_FOR_MODEL).

    This is where we recompute engineered features like:
      - dance_over_tempo
      - energy_dance
      - energy_over_acoustic
      - energy_sq
      - energy_valence
      - valence_dance
      - speech_energy
      - tempo_sq
      - valence_sq

    Anything unknown will be set to NaN and handled by SimpleImputer.
    """
    if FEATURE_NAMES_FOR_MODEL is None:
        # Simple path: just pass through whatever base features we have.
        row = {}
        for k in BASE_AUDIO_KEYS:
            if k in base_features:
                row[k] = base_features[k]
        return row

    row = {}

    def get(name, default=0.0):
        return float(base_features.get(name, default))

    tempo = get("tempo", 0.0)
    energy = get("energy", 0.0)
    valence = get("valence", 0.0)
    dance = get("danceability", 0.0)
    acoustic = get("acousticness", 0.0)
    speech = get("speechiness", 0.0)

    eps = 1e-6

    for fname in FEATURE_NAMES_FOR_MODEL:
        if fname in base_features:
            # Directly provided feature (tempo, energy, etc.)
            row[fname] = base_features[fname]
        elif fname == "dance_over_tempo":
            row[fname] = dance / (tempo + eps)
        elif fname == "energy_dance":
            row[fname] = energy * dance
        elif fname == "energy_over_acoustic":
            row[fname] = energy / (acoustic + eps)
        elif fname == "energy_sq":
            row[fname] = energy ** 2
        elif fname == "energy_valence":
            row[fname] = energy * valence
        elif fname == "valence_dance":
            row[fname] = valence * dance
        elif fname == "speech_energy":
            row[fname] = speech * energy
        elif fname == "tempo_sq":
            row[fname] = tempo ** 2
        elif fname == "valence_sq":
            row[fname] = valence ** 2
        else:
            # For any other feature the model expects, fill NaN;
            # the pipeline's SimpleImputer will handle it.
            row[fname] = math.nan

    return row


def map_compound_to_mood(compound: float) -> str:
    """
    Simple heuristic to map VADER compound score to 4 moods.
    Replace this with your actual mapping if you had a more complex one.
    """
    if compound <= -0.3:
        return "sad"
    elif compound < 0.1:
        return "chill"
    elif compound < 0.6:
        return "happy"
    else:
        return "hyped"


def predict_audio_mood(model, audio_features: dict):
    """
    Build the proper feature row, run the model, and decode the label
    using label_encoder_classes (if present) or model.classes_.
    """
    # Build features DataFrame exactly matching training
    feat_row = build_feature_row_for_model(audio_features)
    df = pd.DataFrame([feat_row])

    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(df)[0]
        pred_idx = probs.argmax()

        # Prefer label names from joblib if available
        if LABEL_NAMES_FROM_JOBLIB is not None and len(LABEL_NAMES_FROM_JOBLIB) == len(probs):
            label_names = LABEL_NAMES_FROM_JOBLIB
            predicted_mood = label_names[pred_idx]
        else:
            # fall back to model.classes_ if it’s strings
            if hasattr(model, "classes_") and not isinstance(model.classes_[0], (int, float)):
                label_names = list(model.classes_)
                predicted_mood = label_names[pred_idx]
            else:
                # final fallback: numeric -> use MOOD_LABELS
                label_names = MOOD_LABELS
                predicted_mood = label_names[pred_idx]

        confidence = float(probs[pred_idx])
        return predicted_mood, confidence, (probs, label_names)

    # Fallback: no predict_proba
    pred = model.predict(df)[0]
    return str(pred), None, None


def predict_lyrics_mood(analyzer, lyrics: str):
    scores = analyzer.polarity_scores(lyrics)
    compound = scores["compound"]
    mood = map_compound_to_mood(compound)
    return mood, compound, scores


def print_demo_result(song, audio_pred, lyrics_pred=None):
    audio_mood, audio_conf, audio_probs = audio_pred

    print("=" * 70)
    print(f"Song: {song['title']}  (ID: {song['id']})")
    print("-" * 70)

    print("Audio model:")
    if audio_conf is not None:
        print(f"  → Predicted mood: {audio_mood}  (confidence = {audio_conf:.3f})")
    else:
        print(f"  → Predicted mood: {audio_mood}  (no probability available)")

    if audio_probs is not None:
        probs, label_names = audio_probs
        print("  Probabilities:")
        for mood_label, p in zip(label_names, probs):
            print(f"    {mood_label:>6}: {p:.3f}")

    if USE_LYRICS and lyrics_pred is not None:
        lyrics_mood, compound, scores = lyrics_pred
        print("\nLyrics model (VADER):")
        print(f"Predicted mood: {lyrics_mood}  (compound = {compound:.3f})")
        print(f"Sentiment scores: {scores}")

        agreement = "Agree" if audio_mood == lyrics_mood else "Disagree"
        print(f"\nOverall: Audio vs Lyrics = {agreement}")

    print("=" * 70 + "\n")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():
    audio_model = load_audio_model(AUDIO_MODEL_PATH)

    if USE_LYRICS:
        vader = SentimentIntensityAnalyzer()
    else:
        vader = None

    print("Running demo on two songs\n")

    for song in DEMO_SONGS:
        audio_pred = predict_audio_mood(audio_model, song["audio_features"])
        if USE_LYRICS:
            lyrics_pred = predict_lyrics_mood(vader, song["lyrics"])
        else:
            lyrics_pred = None
        print_demo_result(song, audio_pred, lyrics_pred)


if __name__ == "__main__":
    main()
