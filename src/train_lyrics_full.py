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

    print("\nGetting audio predictions...")
    
    pipeline = model_data['pipeline']
    feature_names = model_data['features']
    
    # Get features that exist in dataset
    available_features = [f for f in feature_names if f in df.columns]
    X = df[available_features].copy()
   
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

    
    start_time = time.time()
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load dataset
    print(" Loading dataset...")

    MAX_SONGS = 5000  # Process 5000 songs (can increase if you want more)
    
    if MAX_SONGS:
        print(f"Loading {MAX_SONGS:,} songs...")
        df = pd.read_csv(DATASET_PATH, nrows=MAX_SONGS)
    else:
        print("Loading entire dataset (this may take a while)...")
        df = pd.read_csv(DATASET_PATH)
    
    print(f"Loaded {len(df):,} songs")
    print()
    
    # Check lyrics column
    lyrics_column = 'text'
    if lyrics_column not in df.columns:
        print(" ERROR: Lyrics column not found!")
        return
    
    
    df = df[df[lyrics_column].notna()].copy()
    print(f"Songs with lyrics: {len(df):,}")
    print()
    
    # Get audio predictions
    print("Getting audio predictions from Nadine's model...")
    model_data = load_audio_model(MODEL_PATH)
    if model_data is None:
        return
    
    audio_predictions = get_audio_predictions(df, model_data)
    if audio_predictions is None:
        return
    
    df['audio_prediction'] = audio_predictions
    print("Audio predictions added")
    print()
    
    # Get lyrics predictions 
  
    print(f"Processing {len(df):,} songs...")

    
    # Initialize  classifier
    try:
        classifier = FreeLyricsClassifier()
    except ImportError:
        print("ERROR: VADER not installed!")
        return
    
    # Classify songs 
    df_with_lyrics = classifier.classify_dataset(
        df,
        lyrics_column=lyrics_column,
        song_column='track_name' if 'track_name' in df.columns else 'song',
        artist_column='artists' if 'artists' in df.columns else 'Artist(s)',
        max_songs=None,  
        delay=0  
    )
    
    if df_with_lyrics is None:
        print("❌ ERROR: Could not get lyrics predictions")
        return
    
    print()
    
    # Compare results
    print("Comparing predictions...")
    print()
    
    df_compare = df_with_lyrics.dropna(subset=['audio_prediction', 'lyrics_prediction'])
    
    if len(df_compare) == 0:
        print("ERROR: No songs with both predictions!")
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
    
    # Create visualization
    print("\nCreating visualization...")
    try:
        create_comparison_visualization(
            df_compare,
            audio_pred_col='audio_prediction',
            lyrics_pred_col='lyrics_prediction',
            save_path=str(BASE / "audio_lyrics_comparison_full.png")
        )
    except Exception as e:
        print(f"Warning: Could not create visualization: {e}")
    
    # Save results
    print("\n Saving results...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_compare.to_csv(OUTPUT_PATH, index=False)
    print(f"Results saved to: {OUTPUT_PATH}")
    print()
    
    # Calculate time
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    # Summary
   
    print(f"Processed {len(df_compare):,} songs")
    print(f"Audio vs Lyrics agreement: {results['agreement_pct']:.1f}%")
    if 'audio_accuracy' in results:
        print(f"Audio accuracy: {results['audio_accuracy']*100:.1f}%")
        print(f"Lyrics accuracy: {results['lyrics_accuracy']*100:.1f}%")
    
    print(f"Results saved to: {OUTPUT_PATH}")
    print(f"Visualization saved to: audio_lyrics_comparison_full.png")


if __name__ == "__main__":
    main()


