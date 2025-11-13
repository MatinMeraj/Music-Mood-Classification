"""
Main script to run lyrics-based mood classification and compare with audio predictions
Simple and clear implementation for Milestone 2
"""

import pandas as pd
from pathlib import Path
import os
import joblib
import sys

# Import our modules
from lyrics_classifier_free import FreeLyricsClassifier
from compare_audio_lyrics import compare_predictions, create_comparison_visualization

# Setup paths
BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data" / "processed"
MODEL_DIR = BASE / "models"

# File paths
DATASET_PATH = DATA_DIR / "songs_mapped.csv"  # Nadine's fixed dataset
MODEL_PATH = MODEL_DIR / "new_song_mood_model.joblib"  # Audio model from train_from_mapped.py
OUTPUT_PATH = DATA_DIR / "songs_with_predictions.csv"  # Output with both predictions


def load_audio_model(model_path):
    """
    Load the trained audio model.
    """
    print(f"Loading audio model from {model_path}...")
    
    if not model_path.exists():
        print(f"ERROR: Model not found at {model_path}")
        print("Please run train_from_mapped.py first to train the audio model.")
        return None
    
    try:
        model_data = joblib.load(model_path)
        print("Model loaded successfully!")
        return model_data
    except Exception as e:
        print(f"ERROR loading model: {e}")
        return None


def get_audio_predictions(df, model_data):
    """
    Get predictions from the audio model.
    
    Args:
        df: DataFrame with audio features
        model_data: Loaded model data (pipeline + features)
    
    Returns:
        List of predictions
    """
    print("\nGetting audio predictions...")
    
    # Get the pipeline and feature names
    pipeline = model_data['pipeline']
    feature_names = model_data['features']
    
    # Check if we have the required features
    missing_features = [f for f in feature_names if f not in df.columns]
    if missing_features:
        print(f"WARNING: Missing features: {missing_features}")
        print("Some predictions may not be accurate.")
    
    # Get features that exist in the dataset
    available_features = [f for f in feature_names if f in df.columns]
    
    if not available_features:
        print("ERROR: No required features found in dataset!")
        return None
    
    # Prepare features
    X = df[available_features].copy()
    
    # Fill missing features with 0 (or you can use median/mean)
    for feature in feature_names:
        if feature not in X.columns:
            X[feature] = 0  # Simple fallback
    
    # Reorder columns to match model's expected order
    X = X[feature_names]
    
    # Get predictions
    try:
        predictions = pipeline.predict(X)
        print(f"Got {len(predictions)} audio predictions")
        return predictions
    except Exception as e:
        print(f"ERROR getting predictions: {e}")
        return None


def get_lyrics_predictions(df, max_songs=None):
    """
    Get predictions from the FREE lyrics classifier (VADER).
    
    Args:
        df: DataFrame with lyrics
        max_songs: Maximum number of songs to classify (None = all songs)
                   VADER is free and fast, so we can process all songs!
    
    Returns:
        DataFrame with lyrics predictions added
    """
    print("\nGetting lyrics predictions using VADER (FREE)...")
    
    # Check if lyrics column exists
    lyrics_column = 'text'  # Common column name for lyrics
    if lyrics_column not in df.columns:
        # Try other possible column names
        possible_names = ['lyrics', 'Lyrics', 'text', 'Text', 'song_text']
        lyrics_column = None
        for name in possible_names:
            if name in df.columns:
                lyrics_column = name
                break
        
        if lyrics_column is None:
            print("ERROR: Lyrics column not found in dataset!")
            print(f"Available columns: {list(df.columns)}")
            return None
    
    print(f"Using lyrics column: {lyrics_column}")
    
    # Initialize FREE lyrics classifier (VADER)
    try:
        classifier = FreeLyricsClassifier()
    except ImportError as e:
        print(f"ERROR: {e}")
        print("Please install VADER: pip install vaderSentiment")
        return None
    
    # Classify songs (no delay needed - it's free and local!)
    if max_songs:
        print(f"Classifying {max_songs} songs...")
    else:
        print(f"Classifying all {len(df)} songs...")
    print("Using FREE VADER sentiment analysis (no API costs, runs locally!)")
    print()
    
    df_with_predictions = classifier.classify_dataset(
        df,
        lyrics_column=lyrics_column,
        song_column='track_name' if 'track_name' in df.columns else None,
        artist_column='artists' if 'artists' in df.columns else None,
        max_songs=max_songs,
        delay=0  # No delay needed for VADER
    )
    
    return df_with_predictions


def main():
    """
    Main function to run the comparison.
    """
    print("=" * 60)
    print("Audio vs Lyrics Mood Classification Comparison")
    print("=" * 60)
    print()
    
    # Step 1: Load dataset
    print("Step 1: Loading dataset...")
    print(f"Loading from {DATASET_PATH}...")
    print("(This may take a moment for large datasets...)")
    if not DATASET_PATH.exists():
        print(f"ERROR: Dataset not found at {DATASET_PATH}")
        print("Please make sure the dataset exists.")
        print("You may need to download it from Google Drive (as mentioned by Nadine).")
        return
    
    df = pd.read_csv(DATASET_PATH)
    print(f"✓ Loaded {len(df)} songs from dataset")
    print(f"Columns: {list(df.columns)}")
    print()
    
    # Step 2: Get audio predictions
    print("Step 2: Getting audio predictions...")
    model_data = load_audio_model(MODEL_PATH)
    
    if model_data is None:
        print("ERROR: Could not load audio model.")
        print("Please run train_from_mapped.py first to train the model.")
        return
    
    audio_predictions = get_audio_predictions(df, model_data)
    
    if audio_predictions is None:
        print("ERROR: Could not get audio predictions.")
        return
    
    # Add audio predictions to dataframe
    df['audio_prediction'] = audio_predictions
    print("Audio predictions added to dataset")
    print()
    
    # Step 3: Get lyrics predictions using FREE VADER
    print("Step 3: Getting lyrics predictions...")
    print("Using FREE VADER sentiment analysis (no API costs, runs locally!)")
    print("Processing all songs with lyrics...")
    print()
    
    df_with_lyrics = get_lyrics_predictions(df, max_songs=None)  # Process all songs
    
    if df_with_lyrics is None:
        print("ERROR: Could not get lyrics predictions.")
        return
    
    # Step 4: Compare predictions
    print("\nStep 4: Comparing predictions...")
    results = compare_predictions(
        df_with_lyrics,
        audio_pred_col='audio_prediction',
        lyrics_pred_col='lyrics_prediction',
        true_label_col='mood' if 'mood' in df_with_lyrics.columns else None
    )
    
    # Step 5: Create visualization
    print("\nStep 5: Creating visualization...")
    create_comparison_visualization(
        df_with_lyrics,
        audio_pred_col='audio_prediction',
        lyrics_pred_col='lyrics_prediction',
        save_path=str(BASE / "audio_lyrics_comparison.png")
    )
    
    # Step 6: Save results
    print("\nStep 6: Saving results...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_with_lyrics.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved results to {OUTPUT_PATH}")
    
    print("\n" + "=" * 60)
    print("Comparison complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

