import pandas as pd
from pathlib import Path

from enhanced_visualizations import (
    plot_low_confidence_by_mood,
    plot_low_confidence_hist,
)

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data" / "processed"
FIG_DIR = BASE / "figures"

def main():
    csv_path = DATA_DIR / "songs_with_predictions.csv"
    print(f"Loading {csv_path} ...")
    df = pd.read_csv(csv_path)

    #updated threshold
    NEW_AUDIO_LOW_CONF_THRESHOLD = 0.4

    # Recompute audio low-confidence flag
    if "audio_confidence" not in df.columns:
        raise ValueError("audio_confidence column missing in songs_with_predictions.csv")

    df["audio_low_confidence"] = df["audio_confidence"] < NEW_AUDIO_LOW_CONF_THRESHOLD

    FIG_DIR.mkdir(parents=True, exist_ok=True)

    print("Recreating uncertainty plots with threshold 0.4 ...")
    plot_low_confidence_by_mood(
        df,
        save_path=str(FIG_DIR / "uncertainty_by_mood.png"),
    )
    plot_low_confidence_hist(
        df,
        model="audio",
        save_path=str(FIG_DIR / "audio_low_conf_hist.png"),
    )
    # Optional: if you also want lyrics unchanged
    plot_low_confidence_hist(
        df,
        model="lyrics",
        save_path=str(FIG_DIR / "lyrics_low_conf_hist.png"),
    )

    print("Done! Updated PNGs saved in figures/")

if __name__ == "__main__":
    main()
