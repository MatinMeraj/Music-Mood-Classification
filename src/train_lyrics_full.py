"""
Train/Process lyrics classifier on larger dataset
FREE version using VADER - can process entire dataset for free!
"""

import pandas as pd
import sys
from pathlib import Path
import joblib
import time
from datetime import datetime

# Import our modules
sys.path.append(str(Path(__file__).parent))
from lyrics_classifier_free import FreeLyricsClassifier
from compare_audio_lyrics import compare_predictions, create_comparison_visualization

# Setup paths
BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data" / "processed"
MODEL_DIR = BASE / "models"

DATASET_PATH = DATA_DIR / "songs_mapped.csv"
MODEL_PATH = MODEL_DIR / "new_song_mood_model.joblib"
OUTPUT_PATH = DATA_DIR / "audio_lyrics_comparison_full.csv"

def load_audio_model(model_path):
    """Load the trained audio model"""
    print(f"Loading audio model from {model_path}...")
    if not model_path.exists():
        print(f"ERROR: Model not found at {model_path}")
        return None
    
    try:
        model_data = joblib.load(model_path)
        print("✅ Audio model loaded successfully!")
        return model_data
    except Exception as e:
        print(f"ERROR loading model: {e}")
        return None

def get_audio_predictions(df, model_data):
    """Get predictions from the audio model"""
    print("\nGetting audio predictions...")
    
    pipeline = model_data['pipeline']
    feature_names = model_data['features']
    
    # Get features that exist in dataset
    available_features = [f for f in feature_names if f in df.columns]
    X = df[available_features].copy()
    
    # Fill missing features
    for feature in feature_names:
        if feature not in X.columns:
            X[feature] = 0
    
    X = X[feature_names]
    
    # Get predictions
    try:
        predictions = pipeline.predict(X)
        print(f"✅ Got {len(predictions)} audio predictions")
        return predictions
    except Exception as e:
        print(f"ERROR getting predictions: {e}")
        return None

def main():
    """Process larger dataset with lyrics classifier"""
    print("=" * 60)
    print("Lyrics Classifier - Full Processing")
    print("FREE version using VADER (no API costs!)")
    print("=" * 60)
    print()
    
    start_time = time.time()
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Load dataset
    print("Step 1: Loading dataset...")
    
    # Process larger sample - can adjust this number
    # Options: 1000, 5000, 10000, or None for all
    MAX_SONGS = 5000  # Process 5000 songs (can increase if you want more)
    
    if MAX_SONGS:
        print(f"Loading {MAX_SONGS:,} songs...")
        df = pd.read_csv(DATASET_PATH, nrows=MAX_SONGS)
    else:
        print("Loading entire dataset (this may take a while)...")
        df = pd.read_csv(DATASET_PATH)
    
    print(f"✅ Loaded {len(df):,} songs")
    print()
    
    # Check lyrics column
    lyrics_column = 'text'
    if lyrics_column not in df.columns:
        print("❌ ERROR: Lyrics column not found!")
        return
    
    # Filter songs with lyrics
    df = df[df[lyrics_column].notna()].copy()
    print(f"✅ Songs with lyrics: {len(df):,}")
    print()
    
    # Step 2: Get audio predictions
    print("Step 2: Getting audio predictions from Nadine's model...")
    model_data = load_audio_model(MODEL_PATH)
    if model_data is None:
        return
    
    audio_predictions = get_audio_predictions(df, model_data)
    if audio_predictions is None:
        return
    
    df['audio_prediction'] = audio_predictions
    print("✅ Audio predictions added")
    print()
    
    # Step 3: Get lyrics predictions (FREE!)
    print("Step 3: Getting lyrics predictions (FREE VADER)...")
    print(f"💰 Cost: $0.00 (runs locally, no API needed!)")
    print(f"Processing {len(df):,} songs...")
    print("(This may take a while, but it's FREE!)")
    print()
    
    # Initialize FREE classifier
    try:
        classifier = FreeLyricsClassifier()
    except ImportError:
        print("❌ ERROR: VADER not installed!")
        print("Install it with: pip install vaderSentiment")
        return
    
    # Classify songs (FREE, no delay needed!)
    df_with_lyrics = classifier.classify_dataset(
        df,
        lyrics_column=lyrics_column,
        song_column='track_name' if 'track_name' in df.columns else 'song',
        artist_column='artists' if 'artists' in df.columns else 'Artist(s)',
        max_songs=None,  # Process all songs in df
        delay=0  # No delay needed, it's FREE!
    )
    
    if df_with_lyrics is None:
        print("❌ ERROR: Could not get lyrics predictions")
        return
    
    print()
    
    # Step 4: Compare results
    print("Step 4: Comparing predictions...")
    print()
    
    df_compare = df_with_lyrics.dropna(subset=['audio_prediction', 'lyrics_prediction'])
    
    if len(df_compare) == 0:
        print("❌ ERROR: No songs with both predictions!")
        return
    
    print(f"Comparing {len(df_compare):,} songs...")
    print()
    
    # Compare predictions
    results = compare_predictions(
        df_compare,
        audio_pred_col='audio_prediction',
        lyrics_pred_col='lyrics_prediction',
        true_label_col='mood' if 'mood' in df_compare.columns else None
    )
    
    # Step 5: Create visualization
    print("\nStep 5: Creating visualization...")
    try:
        create_comparison_visualization(
            df_compare,
            audio_pred_col='audio_prediction',
            lyrics_pred_col='lyrics_prediction',
            save_path=str(BASE / "audio_lyrics_comparison_full.png")
        )
    except Exception as e:
        print(f"⚠️  Warning: Could not create visualization: {e}")
    
    # Step 6: Save results
    print("\nStep 6: Saving results...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_compare.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Results saved to: {OUTPUT_PATH}")
    print()
    
    # Calculate time
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✅ Processed {len(df_compare):,} songs")
    print(f"✅ Audio vs Lyrics agreement: {results['agreement_pct']:.1f}%")
    if 'audio_accuracy' in results:
        print(f"✅ Audio accuracy: {results['audio_accuracy']*100:.1f}%")
        print(f"✅ Lyrics accuracy: {results['lyrics_accuracy']*100:.1f}%")
    print(f"💰 Cost: $0.00 (FREE!)")
    print(f"⏱️  Time: {minutes}m {seconds}s")
    print(f"✅ Results saved to: {OUTPUT_PATH}")
    print(f"✅ Visualization saved to: audio_lyrics_comparison_full.png")
    print()
    print("=" * 60)
    print("Done! Ready for Discord update and analysis.")
    print("=" * 60)

if __name__ == "__main__":
    main()

