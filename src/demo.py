import math
import joblib
import pandas as pd
from pathlib import Path

USE_LYRICS = True
if USE_LYRICS:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# IMPORT DATA UTILS 

import audio_data  # your existing module
from audio_data import normalize_features, TARGETS

# Full mapped dataset (500k)
FULL_DATA_PATH = audio_data.PROCESSED

# Balanced 20k dataset 
BALANCED_PATH = getattr(
    audio_data,
    "BALANCED_PATH",
    FULL_DATA_PATH.parent / "songs_mapped_20k_balanced.csv",
)


# CONFIG


# Base path
BASE = Path(__file__).resolve().parents[1]

# Path to trained audio model pipeline 
AUDIO_MODEL_PATH = BASE / "models" / "new_song_mood_model.joblib"

# Fallback label order 
MOOD_LABELS = ["happy", "chill", "sad", "hyped"]

# Base audio features we expect in the dataset
BASE_AUDIO_KEYS = [
    "tempo",
    "energy",
    "valence",
    "danceability",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "loudness",
]

# this will dynamically filled after loading the model
FEATURE_NAMES_FOR_MODEL = None
LABEL_NAMES_FROM_JOBLIB = None


#load the model


def load_audio_model(path: Path):

    global FEATURE_NAMES_FOR_MODEL, LABEL_NAMES_FROM_JOBLIB

    print(f"[INFO] Loading audio model from: {path}")
    obj = joblib.load(path)
    print(f"[INFO] Raw loaded object type: {type(obj)}")


    if hasattr(obj, "predict"):
        model = obj
        print("[INFO] Loaded object is a model with .predict().")
        FEATURE_NAMES_FOR_MODEL = (
            list(model.feature_names_in_) if hasattr(model, "feature_names_in_") else None
        )
        LABEL_NAMES_FROM_JOBLIB = None
        return model
    
    if isinstance(obj, dict):
        print(f"[INFO] Loaded a dict with keys: {list(obj.keys())}")

        # Label names from label encoder
        if "label_encoder_classes" in obj:
            LABEL_NAMES_FROM_JOBLIB = list(obj["label_encoder_classes"])
            print(f"label_encoder_classes: {LABEL_NAMES_FROM_JOBLIB}")
        else:
            LABEL_NAMES_FROM_JOBLIB = None
            print("No label_encoder_classes found; will fall back to model.classes_.")

        #find the actual
        model = None
        for key, val in obj.items():
            if hasattr(val, "predict"):
                model = val
                print(f"Found model inside dict at key: '{key}'")
                break

        if model is None:
            raise TypeError(
                "Loaded dict does not contain a usable model with .predict(). "
                f"Available keys: {list(obj.keys())}"
            )

        # Feature names from training, if available
        if hasattr(model, "feature_names_in_"):
            FEATURE_NAMES_FOR_MODEL = list(model.feature_names_in_)
            print(f"feature_names_in_ from model: {FEATURE_NAMES_FOR_MODEL}\n")
        else:
            FEATURE_NAMES_FOR_MODEL = None
            print("Model has no feature_names_in_; will fall back to base keys.\n")

        return model

    # Anything else:
    raise TypeError(
        f"Unexpected object type loaded from {path}: {type(obj)}. "
        "Expected a sklearn estimator or a dict containing one."
    )


#feature engineer for one song 


def build_feature_row_for_model(base_features: dict) -> dict:
    if FEATURE_NAMES_FOR_MODEL is None:
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
            row[fname] = math.nan  # let SimpleImputer handle this

    return row



#lyrics mood from vader

def map_compound_to_mood(compound: float) -> str:
    if compound <= -0.3:
        return "sad"
    elif compound < 0.1:
        return "chill"
    elif compound < 0.6:
        return "happy"
    else:
        return "hyped"


def predict_audio_mood(model, audio_features: dict):
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


#pick songs that are in holdout


def build_key(df: pd.DataFrame) -> pd.Series:

    cols = set(df.columns)
    if {"track_name", "artists"} <= cols:
        return df["track_name"].astype(str) + " || " + df["artists"].astype(str)
    elif "track_name" in cols:
        return df["track_name"].astype(str)
    elif "id" in cols:
        return df["id"].astype(str)
    else:
        return df.index.astype(str)


def load_holdout_demo_songs(n: int = 2):
    print(f"Loading full dataset from: {FULL_DATA_PATH}")
    full = pd.read_csv(FULL_DATA_PATH)
    full = normalize_features(full)

    print(f"Loading balanced 20k dataset from: {BALANCED_PATH}")
    balanced = pd.read_csv(BALANCED_PATH)
    balanced = normalize_features(balanced)

    # Filter to target moods only (optional but clean)
    if "mood" in full.columns:
        full = full[full["mood"].isin(TARGETS)].copy()

    # Identify holdout songs = full - balanced
    full["_key"] = build_key(full)
    balanced["_key"] = build_key(balanced)

    holdout = full[~full["_key"].isin(balanced["_key"])].copy()
    print(f"Holdout size (full - balanced): {len(holdout)} rows")

    if holdout.empty:
        print("Holdout set is empty, falling back to random rows from full dataset.")
        holdout = full.copy()

    # Find lyrics column if present
    lyrics_col = None
    for cand in ["text", "lyrics", "Lyrics"]:
        if cand in holdout.columns:
            lyrics_col = cand
            break

    if lyrics_col is None and USE_LYRICS:
        print("No lyrics column found; demo will run audio-only.")

    # Sample n songs
    n_sample = min(n, len(holdout))
    demo_rows = holdout.sample(n=n_sample, random_state=42)

    demo_songs = []
    for _, row in demo_rows.iterrows():
        audio_features = {}
        for key in BASE_AUDIO_KEYS:
            if key in row.index:
                audio_features[key] = row[key]

        demo_songs.append({
            "id": row.get("track_id", row.get("id", "unknown")),
            "title": row.get("track_name", "Unknown title"),
            "audio_features": audio_features,
            "lyrics": row[lyrics_col] if lyrics_col is not None else "",
        })

    return demo_songs



def print_demo_result(song, audio_pred, lyrics_pred=None):
    audio_mood, audio_conf, audio_probs = audio_pred

    
    print(f"Song: {song['title']}  (ID: {song['id']})")


    print("Audio model:")
    if audio_conf is not None:
        print(f"  -> Predicted mood: {audio_mood}  (confidence = {audio_conf:.3f})")
    else:
        print(f"  -> Predicted mood: {audio_mood}  (no probability available)")

    if audio_probs is not None:
        probs, label_names = audio_probs
        print("  Probabilities:")
        for mood_label, p in zip(label_names, probs):
            print(f"    {mood_label:>6}: {p:.3f}")

    if USE_LYRICS and lyrics_pred is not None:
        lyrics_mood, compound, scores = lyrics_pred
        print("\nLyrics model (VADER):")
        print(f"  -> Predicted mood: {lyrics_mood}  (compound = {compound:.3f})")
        print(f"  Sentiment scores: {scores}")

        agreement = "Agree" if audio_mood == lyrics_mood else "Disagree"
        print(f"\nOverall: Audio vs Lyrics = {agreement}")

   


def main():
    audio_model = load_audio_model(AUDIO_MODEL_PATH)

    if USE_LYRICS:
        vader = SentimentIntensityAnalyzer()
    else:
        vader = None

    print("Running demo on holdout songs (not used in 20k balanced train/eval)\n")

    demo_songs = load_holdout_demo_songs(n=2)

    for song in demo_songs:
        audio_pred = predict_audio_mood(audio_model, song["audio_features"])
        if USE_LYRICS and song.get("lyrics"):
            lyrics_pred = predict_lyrics_mood(vader, song["lyrics"])
        else:
            lyrics_pred = None
        print_demo_result(song, audio_pred, lyrics_pred)


if __name__ == "__main__":
    main()
