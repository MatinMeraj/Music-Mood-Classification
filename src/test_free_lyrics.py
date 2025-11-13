"""
Quick test with FREE lyrics classifier (VADER)
No API needed, no cost!
"""

import pandas as pd
import sys
from pathlib import Path
import joblib

# Import our modules
sys.path.append(str(Path(__file__).parent))
from lyrics_classifier_free import FreeLyricsClassifier
from compare_audio_lyrics import compare_predictions

# Setup paths
BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data" / "processed"
MODEL_DIR = BASE / "models"

DATASET_PATH = DATA_DIR / "songs_mapped.csv"
MODEL_PATH = MODEL_DIR / "new_song_mood_model.joblib"

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
    """Main function for FREE testing"""
    print("=" * 60)
    print("FREE TEST: Lyrics Classifier (VADER)")
    print("No API needed, no cost!")
    print("=" * 60)
    print()
    
    # Step 1: Load dataset
    print("Step 1: Loading dataset...")
    TEST_SONGS = 100  # Test on 100 songs (FREE, no limit!)
    df = pd.read_csv(DATASET_PATH, nrows=TEST_SONGS)
    print(f"✅ Loaded {len(df)} songs for testing")
    print()
    
    # Check lyrics column
    lyrics_column = 'text'
    if lyrics_column not in df.columns:
        print("❌ ERROR: Lyrics column not found!")
        return
    
    print(f"✅ Using lyrics column: {lyrics_column}")
    print(f"✅ Songs with lyrics: {df[lyrics_column].notna().sum()}/{len(df)}")
    print()
    
    # Step 2: Get audio predictions
    print("Step 2: Getting audio predictions...")
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
    print("💰 Cost: $0.00 (runs locally, no API needed!)")
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
        max_songs=TEST_SONGS,
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
    
    print(f"Comparing {len(df_compare)} songs...")
    print()
    
    # Calculate agreement
    agreement = (df_compare['audio_prediction'] == df_compare['lyrics_prediction']).sum()
    agreement_pct = (agreement / len(df_compare)) * 100
    
    print("=" * 60)
    print("RESULTS (FREE Test)")
    print("=" * 60)
    print(f"Songs tested: {len(df_compare)}")
    print(f"Agreement: {agreement}/{len(df_compare)} ({agreement_pct:.1f}%)")
    print(f"Disagreement: {len(df_compare) - agreement}/{len(df_compare)} ({100 - agreement_pct:.1f}%)")
    print()
    
    # Show examples
    print("Sample predictions:")
    print()
    for idx, row in df_compare.head(10).iterrows():
        song_name = row.get('track_name', row.get('song', 'Unknown'))[:30]
        audio_pred = row['audio_prediction']
        lyrics_pred = row['lyrics_prediction']
        true_label = row.get('mood', 'Unknown')
        
        match = "✅" if audio_pred == lyrics_pred else "❌"
        print(f"{match} {song_name:30s} | Audio: {audio_pred:6s} | Lyrics: {lyrics_pred:6s} | True: {true_label}")
    
    print()
    
    # If true labels exist, show accuracy
    if 'mood' in df_compare.columns:
        from sklearn.metrics import accuracy_score
        audio_accuracy = accuracy_score(df_compare['mood'], df_compare['audio_prediction'])
        lyrics_accuracy = accuracy_score(df_compare['mood'], df_compare['lyrics_prediction'])
        
        print("Accuracy (compared to true labels):")
        print(f"  Audio model:  {audio_accuracy:.1%} ({audio_accuracy*100:.1f}%)")
        print(f"  Lyrics model: {lyrics_accuracy:.1%} ({lyrics_accuracy*100:.1f}%)")
        print()
    
    # Save results
    output_path = DATA_DIR / "free_test_results.csv"
    df_compare.to_csv(output_path, index=False)
    print(f"✅ Results saved to: {output_path}")
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY FOR DISCORD")
    print("=" * 60)
    print(f"✅ Tested {len(df_compare)} songs with FREE lyrics classifier")
    print(f"✅ Audio vs Lyrics agreement: {agreement_pct:.1f}%")
    if 'mood' in df_compare.columns:
        print(f"✅ Audio accuracy: {audio_accuracy*100:.1f}%")
        print(f"✅ Lyrics accuracy: {lyrics_accuracy*100:.1f}%")
    print(f"💰 Cost: $0.00 (FREE, no API needed!)")
    print()
    print("✅ Using VADER sentiment analysis (free, local)")
    print("✅ Can test on entire dataset for free!")
    print("=" * 60)

if __name__ == "__main__":
    main()

