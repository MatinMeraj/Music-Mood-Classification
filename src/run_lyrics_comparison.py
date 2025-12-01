import pandas as pd
from pathlib import Path
import os
import joblib
import sys
import numpy as np

from lyrics_classifier_free import FreeLyricsClassifier
from compare_audio_lyrics import compare_predictions, create_comparison_visualization
from enhanced_visualizations import (
    plot_audio_confidence_distribution,
    plot_lyrics_confidence_distribution,
    plot_audio_confidence_by_mood,
    plot_lyrics_confidence_by_mood,
    plot_mood_map,
    plot_audio_prediction_distribution,
    plot_lyrics_prediction_distribution,
    plot_audio_lyrics_agreement_pie,
    plot_audio_lyrics_distribution_comparison,
    plot_audio_lyrics_confusion_matrix,
    plot_audio_agreement_by_mood,
    plot_lyrics_agreement_by_mood,
    plot_audio_confusion_matrix_vs_true,
    plot_lyrics_confusion_matrix_vs_true,
    plot_low_confidence_by_mood,
    plot_low_confidence_hist,
)

# Setup paths
BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data" / "processed"
MODEL_DIR = BASE / "models"


DATASET_PATH = DATA_DIR / "songs_mapped_20k_balanced.csv"
MODEL_PATH = MODEL_DIR / "new_song_mood_model.joblib" 
OUTPUT_PATH = DATA_DIR / "songs_with_predictions.csv"  


AUDIO_LOW_CONF_THRESHOLD = 0.35  
AUDIO_BORDERLINE_MARGIN = 0.15
LYRICS_LOW_CONF_THRESHOLD = 0.6  


TEST_MAX_SONGS = None 


def load_audio_model(model_path):
    
    print(f"Loading audio model from {model_path}...")
    
    if not model_path.exists():
        print(f"ERROR: Model not found at {model_path}")
        print("Please run train_audio_model.py first to train the audio model.")
        return None
    
    try:
        model_data = joblib.load(model_path)
        print("Model loaded successfully!")
        return model_data
    except Exception as e:
        print(f"ERROR loading model: {e}")
        return None


def get_audio_predictions(df, model_data):
    
    print("\nGetting audio predictions...")
    
    # Get the pipeline and feature names
    pipeline = model_data['pipeline']
    feature_names = model_data['features']
    
    missing_features = [f for f in feature_names if f not in df.columns]
    if missing_features:
        print(f"WARNING: Missing features: {missing_features}")
        print("Some predictions may not be accurate.")
    
    # Get features that exist in the dataset
    available_features = [f for f in feature_names if f in df.columns]
    
    if not available_features:
        print("ERROR: No required features found in dataset!")
        return None
    

    X = df[available_features].copy()
    
    # Fill missing features with 0 
    for feature in feature_names:
        if feature not in X.columns:
            X[feature] = 0 
    
  
    X = X[feature_names]
    
    # Get predictions and probabilities for uncertainty estimation
    try:
      
        predictions = pipeline.predict(X)
        
        proba = pipeline.predict_proba(X)
        classes = pipeline.classes_

    
        sorted_idx = np.argsort(proba, axis=1)
        top1_idx = sorted_idx[:, -1]
        top2_idx = sorted_idx[:, -2]

        max_conf = proba[np.arange(len(proba)), top1_idx]
        second_conf = proba[np.arange(len(proba)), top2_idx]
        margin = max_conf - second_conf
        second_labels = classes[top2_idx]

        # Validate confidence values (should be in [0, 1])
        max_conf = np.clip(max_conf, 0, 1)
        second_conf = np.clip(second_conf, 0, 1)
        margin = np.clip(margin, 0, 1)  # Margin should also be in [0, 1]
        
        # Replace any NaN/Infinity values with safe defaults
        max_conf = np.nan_to_num(max_conf, nan=0.0, posinf=1.0, neginf=0.0)
        second_conf = np.nan_to_num(second_conf, nan=0.0, posinf=1.0, neginf=0.0)
        margin = np.nan_to_num(margin, nan=0.0, posinf=1.0, neginf=0.0)

        print(f"Got {len(predictions)} audio predictions")
        return {
            "predictions": predictions,
            "confidence": max_conf,
            "second_choice": second_labels,
            "second_confidence": second_conf,
            "margin": margin,
        }
    except Exception as e:
        print(f"ERROR getting predictions: {e}")
        return None


def get_lyrics_predictions(df, max_songs=None):
    print("\nGetting lyrics predictions using VADER (FREE)...")
    
    lyrics_column = 'text'  
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
    

    try:
        classifier = FreeLyricsClassifier()
    except ImportError as e:
        print(f"ERROR: {e}")
        print("Please install VADER: pip install vaderSentiment")
        return None
    
    # Classify songs
    if max_songs:
        print(f"Classifying {max_songs} songs...")
    else:
        print(f"Classifying all {len(df)} songs...")
    print("Using FREE VADER sentiment analysis  ")
    print()
    
    df_with_predictions = classifier.classify_dataset(
        df,
        lyrics_column=lyrics_column,
        song_column='track_name' if 'track_name' in df.columns else None,
        artist_column='artists' if 'artists' in df.columns else None,
        max_songs=max_songs,
        delay=0  
    )
    
    return df_with_predictions


def main():
    print("Audio vs Lyrics Mood Classification Comparison")

    
    # Load dataset
    print("Step 1: Loading dataset...")
    print(f"Loading from {DATASET_PATH}...")
    print("(This may take a moment for large datasets...)")
    if not DATASET_PATH.exists():
        print(f"ERROR: Dataset not found at {DATASET_PATH}")
        print("Please make sure the dataset exists.")
        print("You may need to download it from Google Drive (as mentioned by Nadine).")
        return
    
    # TEST MODE Only read first N rows for quick testing
    if TEST_MAX_SONGS is not None:
        print(f"TEST MODE: Loading only first {TEST_MAX_SONGS} songs...")
        df = pd.read_csv(DATASET_PATH, nrows=TEST_MAX_SONGS)
        print(f"Loaded {len(df)} songs from dataset (TEST MODE)")
    else:
        df = pd.read_csv(DATASET_PATH)
        print(f"Loaded {len(df)} songs from dataset")
    print(f"Columns: {list(df.columns)}")
    print()
    
    # Get audio predictions
    print("Step 2: Getting audio predictions...")
    model_data = load_audio_model(MODEL_PATH)
    
    if model_data is None:
        print("ERROR: Could not load audio model.")
        print("Please run train_audio_model.py first to train the model.")
        return
    
    audio_info = get_audio_predictions(df, model_data)
    
    if audio_info is None:
        print("ERROR: Could not get audio predictions.")
        return
    
    # Validate audio_info structure
    required_keys = ["predictions", "confidence", "second_choice", "second_confidence", "margin"]
    missing_keys = [key for key in required_keys if key not in audio_info]
    if missing_keys:
        print(f"ERROR: Invalid audio_info structure. Missing keys: {missing_keys}")
        return
    
    # Convert numpy arrays to proper types for CSV saving
    df['audio_prediction'] = audio_info["predictions"].astype(str)
    df['audio_confidence'] = audio_info["confidence"].astype(float)
    df['audio_second_choice'] = audio_info["second_choice"].astype(str)
    df['audio_second_confidence'] = audio_info["second_confidence"].astype(float)
    df['audio_margin'] = audio_info["margin"].astype(float)

    df['audio_low_confidence'] = df['audio_confidence'] < AUDIO_LOW_CONF_THRESHOLD

    df['audio_borderline'] = df['audio_margin'] < AUDIO_BORDERLINE_MARGIN

    df['audio_top2_combo'] = df.apply(
        lambda row: f"{row['audio_prediction']}|{row['audio_second_choice']}"
        if row['audio_borderline'] else row['audio_prediction'],
        axis=1,
    )
    print("Audio predictions and uncertainty metrics added to dataset")
    print()
    
    # Get lyrics predictions using  VADER
    print("Step 3: Getting lyrics predictions...")
    print("Using  VADER sentiment analysis")
    print("Processing all songs with lyrics...")
    print()
    
    df_with_lyrics = get_lyrics_predictions(df, max_songs=TEST_MAX_SONGS)  
    
    if df_with_lyrics is None:
        print("ERROR: Could not get lyrics predictions.")
        return
    

    if 'lyrics_confidence' in df_with_lyrics.columns:
        df_with_lyrics['lyrics_low_confidence'] = (
            df_with_lyrics['lyrics_confidence'] < LYRICS_LOW_CONF_THRESHOLD
        )
    
    # Compare predictions
    print("\nStep 4: Comparing predictions...")
    results = compare_predictions(
        df_with_lyrics,
        audio_pred_col='audio_prediction',
        lyrics_pred_col='lyrics_prediction',
        true_label_col='mood' if 'mood' in df_with_lyrics.columns else None
    )
    
    # create basic visualization
    print("\nStep 5: Creating basic comparison visualization...")
    create_comparison_visualization(
        df_with_lyrics,
        audio_pred_col='audio_prediction',
        lyrics_pred_col='lyrics_prediction',
        save_path=str(BASE / "audio_lyrics_comparison.png")
    )
    
    #create enhanced visualizations
    print("\nCreating enhanced visualizations...")
    
    print(" Confidence distributions")
    plot_audio_confidence_distribution(save_path=str(BASE / "figures" / "audio_confidence_distribution.png"))
    plot_lyrics_confidence_distribution(df_with_lyrics, save_path=str(BASE / "figures" / "lyrics_confidence_distribution.png"))
    plot_audio_confidence_by_mood(save_path=str(BASE / "figures" / "audio_confidence_by_mood.png"))
    plot_lyrics_confidence_by_mood(df_with_lyrics, save_path=str(BASE / "figures" / "lyrics_confidence_by_mood.png"))
    # Uncertainty-focused plots 
    print("Uncertainty visualizations")
    plot_low_confidence_by_mood(
        df_with_lyrics,
        save_path=str(BASE / "figures" / "uncertainty_by_mood.png"),
    )
    plot_low_confidence_hist(
        df_with_lyrics,
        model='audio',
        save_path=str(BASE / "figures" / "audio_low_conf_hist.png"),
    )
    plot_low_confidence_hist(
        df_with_lyrics,
        model='lyrics',
        save_path=str(BASE / "figures" / "lyrics_low_conf_hist.png"),
    )
    
    print(" Mood maps ")
    print(" PCA")
    plot_mood_map(df=None, method='pca', n_samples=10000,
                  save_path=str(BASE / "figures" / "mood_map_pca.png"))
    print("t-SNE")
    plot_mood_map(df=None, method='tsne', n_samples=3000,
                  save_path=str(BASE / "figures" / "mood_map_tsne.png"))
    
    print("Audio vs lyrics comparisons")
    plot_audio_prediction_distribution(df_with_lyrics, save_path=str(BASE / "figures" / "audio_prediction_distribution.png"))
    plot_lyrics_prediction_distribution(df_with_lyrics, save_path=str(BASE / "figures" / "lyrics_prediction_distribution.png"))
    plot_audio_lyrics_agreement_pie(df_with_lyrics, save_path=str(BASE / "figures" / "audio_lyrics_agreement_pie.png"))
    plot_audio_lyrics_distribution_comparison(df_with_lyrics, save_path=str(BASE / "figures" / "audio_lyrics_distribution_comparison.png"))
    plot_audio_lyrics_confusion_matrix(df_with_lyrics, save_path=str(BASE / "figures" / "audio_lyrics_confusion_matrix.png"))
    plot_audio_agreement_by_mood(df_with_lyrics, save_path=str(BASE / "figures" / "audio_agreement_by_mood.png"))
    plot_lyrics_agreement_by_mood(df_with_lyrics, save_path=str(BASE / "figures" / "lyrics_agreement_by_mood.png"))
    if 'mood' in df_with_lyrics.columns:
        plot_audio_confusion_matrix_vs_true(df_with_lyrics, save_path=str(BASE / "figures" / "audio_confusion_matrix_vs_true.png"))
        plot_lyrics_confusion_matrix_vs_true(df_with_lyrics, save_path=str(BASE / "figures" / "lyrics_confusion_matrix_vs_true.png"))
    
    # Save results
    print("\nSaving results...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Ensure all prediction columns are strings and confidence columns are floats before saving
    if 'audio_prediction' in df_with_lyrics.columns:
        df_with_lyrics['audio_prediction'] = df_with_lyrics['audio_prediction'].astype(str)
        # Replace 'nan' strings with actual NaN
        df_with_lyrics['audio_prediction'] = df_with_lyrics['audio_prediction'].replace('nan', pd.NA)
    if 'lyrics_prediction' in df_with_lyrics.columns:
        df_with_lyrics['lyrics_prediction'] = df_with_lyrics['lyrics_prediction'].astype(str)
        # Replace 'nan' strings with actual NaN
        df_with_lyrics['lyrics_prediction'] = df_with_lyrics['lyrics_prediction'].replace('nan', pd.NA)
    if 'audio_confidence' in df_with_lyrics.columns:
        df_with_lyrics['audio_confidence'] = pd.to_numeric(df_with_lyrics['audio_confidence'], errors='coerce')
        # Ensure confidence is in valid range [0, 1]
        df_with_lyrics['audio_confidence'] = df_with_lyrics['audio_confidence'].clip(0, 1)
    if 'lyrics_confidence' in df_with_lyrics.columns:
        df_with_lyrics['lyrics_confidence'] = pd.to_numeric(df_with_lyrics['lyrics_confidence'], errors='coerce')
        # Ensure confidence is in valid range [0, 1]
        df_with_lyrics['lyrics_confidence'] = df_with_lyrics['lyrics_confidence'].clip(0, 1)
    
    # Validate required columns exist before saving
    required_cols = ['audio_prediction', 'lyrics_prediction']
    missing_cols = [col for col in required_cols if col not in df_with_lyrics.columns]
    if missing_cols:
        print(f"ERROR: Missing required columns before saving: {missing_cols}")
        print(f"Available columns: {list(df_with_lyrics.columns)}")
        return
    
    # Check for empty dataframe
    if len(df_with_lyrics) == 0:
        print("ERROR: DataFrame is empty, cannot save")
        return
    
    df_with_lyrics.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df_with_lyrics)} rows to {OUTPUT_PATH}")
    print(f"  Columns saved: {len(df_with_lyrics.columns)}")
    print(f"  Required columns present: {all(col in df_with_lyrics.columns for col in required_cols)}")



if __name__ == "__main__":
    main()

