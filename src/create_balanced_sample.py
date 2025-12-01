import pandas as pd
from pathlib import Path
import numpy as np

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data" / "processed"
INPUT_FILE = DATA_DIR / "songs_mapped.csv"
OUTPUT_FILE = DATA_DIR / "songs_balanced_sample.csv"

TARGETS = ["happy", "chill", "sad", "hyped"]
SAMPLES_PER_CLASS = 5000  # Adjust this number based on your needs

def create_balanced_sample(input_path, output_path, samples_per_class=5000):

    print(f"Loading dataset from {input_path}...")
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} total songs")
    
    # Filter to target moods only
    df = df[df['mood'].isin(TARGETS)].copy()
    print(f"Filtered to target moods: {len(df)} songs")
    
    # Get distribution before sampling
    print("\nOriginal distribution:")
    print(df['mood'].value_counts())
    
    # Sample evenly from each class
    sampled_dfs = []
    for mood in TARGETS:
        mood_df = df[df['mood'] == mood].copy()
        if len(mood_df) >= samples_per_class:
            sampled = mood_df.sample(n=samples_per_class, random_state=42)
            print(f"Sampled {samples_per_class} songs from '{mood}' (had {len(mood_df)})")
        else:
            # If class has fewer samples, take all
            sampled = mood_df.copy()
            print(f"Took all {len(mood_df)} songs from '{mood}' (fewer than {samples_per_class})")
        sampled_dfs.append(sampled)
    
    # Combine all samples
    balanced_df = pd.concat(sampled_dfs, ignore_index=True)
    
    # Shuffle the combined dataset
    balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"\nBalanced sample distribution:")
    print(balanced_df['mood'].value_counts())
    print(f"\nTotal balanced sample: {len(balanced_df)} songs")
    
    # Save balanced sample
    output_path.parent.mkdir(parents=True, exist_ok=True)
    balanced_df.to_csv(output_path, index=False)
    print(f"\nSaved balanced sample to {output_path}")
    
    return balanced_df

if __name__ == "__main__":
    create_balanced_sample(INPUT_FILE, OUTPUT_FILE, SAMPLES_PER_CLASS)

