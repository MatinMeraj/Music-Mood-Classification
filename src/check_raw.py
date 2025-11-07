import pandas as pd

df = pd.read_csv("data/spotify_dataset.csv")

# pick one
col = "emotion"  # or "mood"

# normalize (lowercase/strip) then list uniques
moods = (df[col].astype(str)
              .str.strip()
              .str.lower()
              .replace({"nan": pd.NA}))

print("Unique moods:")
print(sorted(moods.dropna().unique().tolist()))

print("\nCounts:")
print(moods.value_counts(dropna=True))