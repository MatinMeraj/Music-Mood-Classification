# src/audio_data.py
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split


BASE = Path(__file__).resolve().parents[1]
PROCESSED = BASE / "data" / "processed" / "songs_mapped.csv"
BALANCED_PATH = BASE / "data" / "processed" / "songs_mapped_20k_balanced.csv"
RANDOM_STATE = 42

#limiting the number of songs per mood from the dataset to 5000 (semantically)
#so in total there are 20k 
MAX_PER_CLASS = 5000

#global variable of the target
TARGETS = ["happy", "chill", "sad", "hyped"]
#features to decide the mood
FEATURE_WISHLIST = [
    "tempo","energy","valence","loudness",
    "danceability","speechiness","acousticness",
    "instrumentalness","liveness"
]

#cleaning up the strings of loudness
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

def balanced_downsample(df: pd.DataFrame,
                        label_col: str = "mood",
                        max_per_class: int = None,
                        random_state: int = RANDOM_STATE) -> pd.DataFrame:
    """
    Downsample each mood class to at most max_per_class rows,
    keeping the class distribution roughly balanced.
    """
    if max_per_class is None:
        return df

    def _sample_group(g: pd.DataFrame) -> pd.DataFrame:
        if len(g) <= max_per_class:
            return g
        return g.sample(n=max_per_class, random_state=random_state)

    return (
        df.groupby(label_col, group_keys=False)
          .apply(_sample_group)
          .reset_index(drop=True)
    )

def load_audio_data():
    if not PROCESSED.exists():
        raise FileNotFoundError(f"Mapped file not found: {PROCESSED}.")

    df = pd.read_csv(PROCESSED)
    df = normalize_features(df)

    if "mood" not in df.columns:
        raise ValueError("Expecting the mood column in the mapped CSV.")

    # keep only target moods
    df = df[df["mood"].isin(TARGETS)].copy()
    if df.empty:
        raise ValueError("After filtering to TARGETS, no rows remain.")

    # downsample to reduce dataset size but keep mood distribution
    df = balanced_downsample(df, label_col="mood", max_per_class=MAX_PER_CLASS, random_state=RANDOM_STATE)
    if df.empty:
        raise ValueError("Dataframe is empty")

    #save the dataset into a new file
    if not BALANCED_PATH.exists():
        df.to_csv(BALANCED_PATH, index=False)
        print(f"Saved balanced dataset ({len(df)} rows) to {BALANCED_PATH}")

    have = [c for c in FEATURE_WISHLIST if c in df.columns]
    if not have:
        raise ValueError(
            "None of the expected audio features are present. "
            f"Looked for: {FEATURE_WISHLIST}"
        )

    for c in have:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # drop all NA features
    all_nan_feats = [c for c in have if df[c].isna().all()]
    if all_nan_feats:
        df = df.drop(columns=all_nan_feats)
        have = [c for c in have if c not in all_nan_feats]
        if not have:
            raise ValueError("all features are NAs")

    X = df[have]
    y = df["mood"].astype(str)

    # train 70%, validate 20%, test 10%
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y,
        test_size=0.10,
        stratify=y,
        random_state=RANDOM_STATE
    )

    # remaining 0.9 goes to train and val: 2/9 =  0.222 for cv
    X_train, X_cv, y_train, y_cv = train_test_split(
        X_temp, y_temp,
        test_size=2/9,
        stratify=y_temp,
        random_state=RANDOM_STATE
    )

    return X_train, X_cv, X_test, y_train, y_cv, y_test, have

