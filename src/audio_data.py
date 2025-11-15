# src/audio_data.py
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

PROCESSED = Path("data/processed/songs_mapped.csv")
RANDOM_STATE = 42

TARGETS = ["happy", "chill", "sad", "hyped"]
FEATURE_WISHLIST = [
    "tempo","energy","valence","loudness",
    "danceability","speechiness","acousticness",
    "instrumentalness","liveness"
]

def clean_loudness(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()
    s = s.str.replace("\u2212", "-", regex=False)
    s = s.str.replace(r"[dD][bB]", "", regex=True)
    s = s.str.replace(r"[^0-9\.\-\+]", "", regex=True)
    return pd.to_numeric(s, errors="coerce").clip(-60, 0)

def normalize_features(df: pd.DataFrame) -> pd.DataFrame:
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

    leak_prefixes = ("Good for ", "Similar ", "Similarity Score")
    drop_cols = [c for c in df.columns if c == "Album" or any(c.startswith(p) for p in leak_prefixes)]
    if drop_cols:
        df = df.drop(columns=drop_cols, errors="ignore")

    return df

def load_audio_data():
    if not PROCESSED.exists():
        raise FileNotFoundError(f"Mapped file not found: {PROCESSED}. Run your map_labels.py first.")

    df = pd.read_csv(PROCESSED)
    df = normalize_features(df)

    if "mood" not in df.columns:
        raise ValueError("Expected 'mood' column in mapped CSV.")

    df = df[df["mood"].isin(TARGETS)].copy()
    if df.empty:
        raise ValueError("After filtering to TARGETS, no rows remain. Check your mapping step.")

    have = [c for c in FEATURE_WISHLIST if c in df.columns]
    if not have:
        raise ValueError(
            "None of the expected audio features are present. "
            f"Looked for: {FEATURE_WISHLIST}"
        )

    for c in have:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # drop all-NaN features
    all_nan_feats = [c for c in have if df[c].isna().all()]
    if all_nan_feats:
        df = df.drop(columns=all_nan_feats)
        have = [c for c in have if c not in all_nan_feats]
        if not have:
            raise ValueError("All candidate features were all-NaN after coercion.")

    X = df[have]
    y = df["mood"].astype(str)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )

    return X_train, X_test, y_train, y_test, have
