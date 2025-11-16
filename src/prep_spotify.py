from pathlib import Path
import pandas as pd

IN_FILE = Path("data/spotify_dataset.csv")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "songs_mapped.csv"

#load raw data
df = pd.read_csv(IN_FILE)
LABEL_COL = "emotion" 

moods = (df[LABEL_COL].astype(str)
                     .str.strip()
                     .str.lower()
                     .replace({"nan": pd.NA}))

df["raw_mood"] = moods

#semantic mapping as it is reasonable to bucket them into the four moods
MOOD_MAP = {
    "joy": "happy",
    "love": "chill",      #love is mapped to chill
    "surprise": "happy",
    "interest": "happy",
    "sadness": "sad",
    "anger": "hyped",
    "angry": "hyped",
    "fear": "hyped",
    "thirst": "hyped",

    # rare/noisy labels
    "true": None,
    "pink": None,
    "confusion": None,
}

#if mood is None, drop the records
df["mood"] = df["raw_mood"].map(MOOD_MAP)

#keep 4 target moods
TARGETS = {"happy", "chill", "sad", "hyped"}
df = df[df["mood"].isin(TARGETS)].copy()

#renaming as a lowercase 
rename = {
    "Tempo": "tempo",
    "Energy": "energy",
    "Positiveness": "valence",
    "Loudness (db)": "loudness",
    "Loudness (dB)": "loudness",
}
for k, v in rename.items():
    if k in df.columns and v not in df.columns:
        df = df.rename(columns={k: v})

for c in ["tempo", "energy", "valence", "loudness"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

#sanity check
print("Class counts after mapping:")
print(df["mood"].value_counts())

#saving the output as song_mapped.csv
df.to_csv(OUT, index=False)
print(f"Saved mapped dataset → {OUT}")