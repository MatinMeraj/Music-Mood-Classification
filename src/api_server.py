"""
Backend API server for Spotify Song Mood Classifier
Flask API to serve model predictions to Next.js frontend
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import sys
import os

# Add src directory to path
sys.path.append(os.path.dirname(__file__))

from run_lyrics_comparison import (
    load_audio_model, 
    get_audio_predictions
)
from lyrics_classifier_free import FreeLyricsClassifier

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Setup paths
BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data" / "processed"
MODEL_DIR = BASE / "models"

# Load model once at startup
MODEL_PATH = MODEL_DIR / "new_song_mood_model.joblib"
model_data = None

# Initialize lyrics classifier
lyrics_classifier = None

# Thresholds
AUDIO_LOW_CONF_THRESHOLD = 0.35
LYRICS_LOW_CONF_THRESHOLD = 0.6

def load_models():
    """Load models once at startup"""
    global model_data, lyrics_classifier
    if model_data is None and MODEL_PATH.exists():
        print("Loading audio model...")
        model_data = load_audio_model(MODEL_PATH)
        print("Audio model loaded!")
    if lyrics_classifier is None:
        try:
            print("Loading lyrics classifier...")
            lyrics_classifier = FreeLyricsClassifier()
            print("Lyrics classifier loaded!")
        except Exception as e:
            print(f"Warning: Could not load lyrics classifier: {e}")
            lyrics_classifier = None

# Load models at startup
load_models()

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    predictions_file = DATA_DIR / "songs_with_predictions.csv"
    return jsonify({
        "status": "ok", 
        "audio_model_loaded": model_data is not None,
        "lyrics_model_loaded": lyrics_classifier is not None,
        "predictions_file_exists": predictions_file.exists()
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Get aggregated statistics for charts and graphs
    Returns data from songs_with_predictions.csv
    """
    try:
        # Try multiple possible file locations
        possible_files = [
            DATA_DIR / "songs_with_predictions.csv",
            BASE / "data" / "processed" / "songs_with_predictions.csv",
            BASE / "songs_with_predictions.csv",
        ]
        
        predictions_file = None
        for file_path in possible_files:
            if file_path.exists():
                predictions_file = file_path
                break
        
        if not predictions_file:
            return jsonify({
                "error": "Predictions file not found. Please run the prediction script first.",
                "searched_paths": [str(p) for p in possible_files]
            }), 404
        
        print(f"Loading predictions from: {predictions_file}")
        df = pd.read_csv(predictions_file)
        print(f"Loaded {len(df)} rows from predictions file")
        
        # Check required columns
        required_cols = ['audio_prediction', 'lyrics_prediction']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return jsonify({
                "error": f"Missing required columns: {missing_cols}",
                "available_columns": list(df.columns)
            }), 400
        
        # Normalize predictions to lowercase strings for consistent comparison
        # Handle both string and object types, and ensure lowercase
        df['audio_prediction'] = df['audio_prediction'].astype(str).str.lower().str.strip()
        df['lyrics_prediction'] = df['lyrics_prediction'].astype(str).str.lower().str.strip()
        
        # Replace 'nan' strings (from NaN conversion) with actual NaN
        df['audio_prediction'] = df['audio_prediction'].replace('nan', pd.NA)
        df['lyrics_prediction'] = df['lyrics_prediction'].replace('nan', pd.NA)
        
        # Filter out rows with NaN predictions for calculations
        df_valid = df.dropna(subset=['audio_prediction', 'lyrics_prediction']).copy()
        total = len(df_valid)
        
        if total == 0:
            return jsonify({
                "error": "No valid predictions found in file (all rows have NaN predictions)",
                "total_rows": len(df)
            }), 400
        
        # Calculate agreement statistics (only on valid rows)
        agreement = (df_valid['audio_prediction'] == df_valid['lyrics_prediction']).sum()
        agreement_pct = (agreement / total * 100) if total > 0 else 0
        
        # Distribution by mood (only on valid rows, exclude NaN)
        audio_dist = df_valid['audio_prediction'].value_counts(normalize=True).to_dict()
        lyrics_dist = df_valid['lyrics_prediction'].value_counts(normalize=True).to_dict()
        
        moods = ['happy', 'chill', 'sad', 'hyped']
        distribution_data = []
        for mood in moods:
            distribution_data.append({
                "mood": mood.capitalize(),
                "audio": round(audio_dist.get(mood, 0) * 100, 1),
                "lyrics": round(lyrics_dist.get(mood, 0) * 100, 1)
            })
        
        # Confusion matrix (audio vs lyrics) - only on valid rows
        confusion_data = []
        for audio_mood in moods:
            row = {"audio": audio_mood.capitalize()}
            for lyrics_mood in moods:
                count = len(df_valid[
                    (df_valid['audio_prediction'] == audio_mood) & 
                    (df_valid['lyrics_prediction'] == lyrics_mood)
                ])
                row[lyrics_mood] = int(count)
            confusion_data.append(row)
        
        # Low confidence statistics (only on valid rows with valid confidence values)
        low_conf_data = []
        if 'audio_confidence' in df_valid.columns and 'lyrics_confidence' in df_valid.columns:
            # Filter out NaN confidence values for accurate calculations
            df_with_conf = df_valid.dropna(subset=['audio_confidence', 'lyrics_confidence']).copy()
            
            for mood in moods:
                audio_mood_df = df_with_conf[df_with_conf['audio_prediction'] == mood]
                lyrics_mood_df = df_with_conf[df_with_conf['lyrics_prediction'] == mood]
                
                # Calculate percentage with low confidence (only on rows with valid confidence)
                audio_pct = (audio_mood_df['audio_confidence'] < AUDIO_LOW_CONF_THRESHOLD).mean() * 100 if len(audio_mood_df) > 0 else 0
                lyrics_pct = (lyrics_mood_df['lyrics_confidence'] < LYRICS_LOW_CONF_THRESHOLD).mean() * 100 if len(lyrics_mood_df) > 0 else 0
                
                low_conf_data.append({
                    "mood": mood.capitalize(),
                    "audio": round(audio_pct, 1),
                    "lyrics": round(lyrics_pct, 1)
                })
        
        # Confidence distribution (only on valid rows with valid confidence values)
        confidence_dist = []
        if 'audio_confidence' in df_valid.columns and 'lyrics_confidence' in df_valid.columns:
            # Filter out NaN confidence values
            df_with_conf = df_valid.dropna(subset=['audio_confidence', 'lyrics_confidence']).copy()
            
            bins = [(0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0)]
            for i, (low, high) in enumerate(bins):
                # For the last bin, include values equal to 1.0
                if i == len(bins) - 1:
                    audio_count = len(df_with_conf[(df_with_conf['audio_confidence'] >= low) & (df_with_conf['audio_confidence'] <= high)])
                    lyrics_count = len(df_with_conf[(df_with_conf['lyrics_confidence'] >= low) & (df_with_conf['lyrics_confidence'] <= high)])
                else:
                    audio_count = len(df_with_conf[(df_with_conf['audio_confidence'] >= low) & (df_with_conf['audio_confidence'] < high)])
                    lyrics_count = len(df_with_conf[(df_with_conf['lyrics_confidence'] >= low) & (df_with_conf['lyrics_confidence'] < high)])
                
                confidence_dist.append({
                    "range": f"{low}-{high}",
                    "audio": int(audio_count),
                    "lyrics": int(lyrics_count)
                })
        
        return jsonify({
            "agreement": {
                "agree": round(agreement_pct, 1),
                "disagree": round(100 - agreement_pct, 1),
                "total": int(total)
            },
            "distribution": distribution_data,
            "confusion": confusion_data,
            "lowConfidence": low_conf_data,
            "confidenceDistribution": confidence_dist
        })
        
    except Exception as e:
        print(f"Error getting stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/dataset', methods=['GET'])
def get_dataset_stats():
    """
    Get dataset distribution statistics
    """
    try:
        # Try to find the main dataset file
        possible_files = [
            DATA_DIR / "songs_mapped.csv",
            DATA_DIR / "songs_mapped_20k_balanced.csv",
            BASE / "data" / "processed" / "songs_mapped.csv",
        ]
        
        dataset_file = None
        for file_path in possible_files:
            if file_path.exists():
                dataset_file = file_path
                break
        
        if not dataset_file:
            return jsonify({
                "error": "Dataset file not found",
                "searched_paths": [str(p) for p in possible_files]
            }), 404
        
        df = pd.read_csv(dataset_file, nrows=100000)  # Sample for speed
        
        if 'mood' not in df.columns:
            return jsonify({
                "error": "Dataset does not contain 'mood' column",
                "available_columns": list(df.columns)
            }), 400
        
        # Filter out NaN values and normalize mood to lowercase for consistent counting
        df_valid = df.dropna(subset=['mood']).copy()
        if len(df_valid) == 0:
            return jsonify({
                "error": "Dataset contains no valid mood values",
                "total_rows": len(df)
            }), 400
        
        # Normalize mood values to lowercase for consistent counting
        df_valid['mood'] = df_valid['mood'].astype(str).str.lower().str.strip()
        
        # Filter to only valid mood values
        valid_moods = ['happy', 'chill', 'sad', 'hyped']
        df_valid = df_valid[df_valid['mood'].isin(valid_moods)]
        
        if len(df_valid) == 0:
            return jsonify({
                "error": "Dataset contains no valid mood values (expected: happy, chill, sad, hyped)",
                "total_rows": len(df),
                "sample_moods": df['mood'].dropna().unique().tolist()[:10] if 'mood' in df.columns else []
            }), 400
        
        # Calculate distribution
        mood_counts = df_valid['mood'].value_counts().to_dict()
        total = len(df_valid)
        
        moods = ['happy', 'chill', 'sad', 'hyped']
        distribution = []
        for mood in moods:
            count = mood_counts.get(mood, 0)
            distribution.append({
                "mood": mood.capitalize(),
                "count": int(count),
                "percentage": round((count / total * 100) if total > 0 else 0, 1)
            })
        
        return jsonify({
            "total": int(total),
            "distribution": distribution
        })
        
    except Exception as e:
        print(f"Error getting dataset stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Predict mood for a song
    
    Request body:
    {
        "song": "string",      # Required: song name
        "artist": "string",    # Optional: artist name
        "audio_features": {    # Optional: if not provided, will try to look up in dataset
            "tempo": float,
            "energy": float,
            "valence": float,
            ...
        },
        "lyrics": "string"     # Optional: lyrics text
    }
    
    Response:
    {
        "song": string,
        "artist": string,
        "audio": {
            "mood": "happy" | "chill" | "sad" | "hyped",
            "confidence": float,
            "lowConfidence": boolean
        },
        "lyrics": {
            "mood": "happy" | "chill" | "sad" | "hyped",
            "confidence": float,
            "lowConfidence": boolean
        },
        "agree": boolean
    }
    """
    try:
        data = request.json
        
        if not data or 'song' not in data:
            return jsonify({"error": "Missing required field: 'song'"}), 400
        
        song_name = data.get('song')
        artist_name = data.get('artist', 'Unknown Artist')
        
        # Get audio features - check if provided, otherwise try to find in dataset
        audio_features = data.get('audio_features')
        
        # If audio features not provided, try to find song in dataset
        if audio_features is None:
            audio_features = find_song_in_dataset(song_name, artist_name)
            if audio_features is None:
                return jsonify({
                    "error": f"Song '{song_name}' not found in dataset. Please provide audio_features.",
                    "required_features": [
                        "tempo", "energy", "valence", "loudness", 
                        "danceability", "speechiness", "acousticness",
                        "instrumentalness", "liveness"
                    ]
                }), 404
        
        # Get lyrics - check if provided, otherwise try to find in dataset
        lyrics = data.get('lyrics')
        if lyrics is None:
            lyrics = find_lyrics_in_dataset(song_name, artist_name)
        
        # Get audio prediction
        audio_result = None
        if model_data is not None:
            try:
                # Prepare features DataFrame
                feature_names = model_data['features']
                feature_dict = {f: audio_features.get(f, 0.0) for f in feature_names}
                df = pd.DataFrame([feature_dict])
                
                # Get prediction
                audio_info = get_audio_predictions(df, model_data)
                if audio_info and "predictions" in audio_info and "confidence" in audio_info:
                    # Handle both array and single value cases
                    if isinstance(audio_info["confidence"], (list, np.ndarray)):
                        confidence = float(audio_info["confidence"][0])
                        prediction = str(audio_info["predictions"][0])
                    else:
                        confidence = float(audio_info["confidence"])
                        prediction = str(audio_info["predictions"])
                    
                    # Normalize mood to lowercase for consistency
                    mood_normalized = str(prediction).lower().strip()
                    
                    # Validate mood is one of expected values
                    valid_moods = ['happy', 'chill', 'sad', 'hyped']
                    if mood_normalized not in valid_moods:
                        print(f"Warning: Unexpected mood value '{mood_normalized}', defaulting to 'happy'")
                        mood_normalized = 'happy'
                    
                    audio_result = {
                        "mood": mood_normalized,
                        "confidence": confidence,
                        "lowConfidence": confidence < AUDIO_LOW_CONF_THRESHOLD
                    }
                else:
                    raise ValueError("Invalid response from get_audio_predictions")
            except Exception as e:
                print(f"Error getting audio prediction: {e}")
                return jsonify({"error": f"Audio prediction failed: {str(e)}"}), 500
        else:
            return jsonify({"error": "Audio model not loaded"}), 500
        
        # Get lyrics prediction
        lyrics_result = None
        if lyrics and lyrics_classifier:
            try:
                mood, confidence = lyrics_classifier.classify_lyrics(lyrics, song_name, artist_name)
                if mood:
                    # Normalize mood to lowercase for consistency
                    mood_normalized = str(mood).lower().strip()
                    
                    # Validate mood is one of expected values
                    valid_moods = ['happy', 'chill', 'sad', 'hyped']
                    if mood_normalized not in valid_moods:
                        print(f"Warning: Unexpected lyrics mood value '{mood_normalized}', defaulting to 'happy'")
                        mood_normalized = 'happy'
                    
                    lyrics_result = {
                        "mood": mood_normalized,
                        "confidence": float(confidence),
                        "lowConfidence": float(confidence) < LYRICS_LOW_CONF_THRESHOLD
                    }
            except Exception as e:
                print(f"Error getting lyrics prediction: {e}")
                # Don't fail if lyrics prediction fails, just skip it
        
        # Check if predictions agree (both moods are normalized to lowercase)
        agree = False
        if audio_result and lyrics_result:
            # Both moods are already normalized to lowercase, so direct comparison is safe
            agree = audio_result["mood"] == lyrics_result["mood"]
        elif not lyrics_result:
            # If no lyrics prediction, just return audio
            agree = None
        
        # Build response
        # Ensure audio_result exists (should always exist if we got here)
        if not audio_result:
            return jsonify({"error": "Failed to generate audio prediction"}), 500
        
        response = {
            "song": song_name,
            "artist": artist_name,
            "audio": audio_result,
            "agree": agree
        }
        
        # Always include lyrics in response, even if None (for consistent API contract)
        if lyrics_result:
            response["lyrics"] = lyrics_result
        else:
            # Return None explicitly for missing lyrics prediction
            response["lyrics"] = None
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in predict endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def find_song_in_dataset(song_name, artist_name):
    """
    Try to find song in dataset and return audio features
    
    Args:
        song_name: Name of the song
        artist_name: Name of the artist (optional)
    
    Returns:
        Dict of audio features or None if not found
    """
    # Try balanced sample first, then full dataset
    for file_name in ["songs_balanced_sample.csv", "songs_mapped.csv", "songs_with_predictions.csv"]:
        file_path = DATA_DIR / file_name
        if file_path.exists():
            try:
                # Read first few rows to search
                df = pd.read_csv(file_path, nrows=50000)  # Search in first 50k rows
                
                # Try to match song name (case-insensitive)
                song_col = None
                artist_col = None
                
                # Find song column
                for col in ['song', 'track_name', 'Song', 'Track Name', 'name']:
                    if col in df.columns:
                        song_col = col
                        break
                
                # Find artist column
                for col in ['artists', 'Artist(s)', 'artist', 'Artist', 'artist_name']:
                    if col in df.columns:
                        artist_col = col
                        break
                
                if song_col:
                    # Search for song
                    mask = df[song_col].str.lower().str.contains(song_name.lower(), na=False)
                    if artist_col:
                        if artist_name and artist_name != 'Unknown Artist':
                            mask = mask & df[artist_col].str.lower().str.contains(artist_name.lower(), na=False)
                    
                    matches = df[mask]
                    if len(matches) > 0:
                        # Take first match
                        song_row = matches.iloc[0]
                        
                        # Extract audio features
                        feature_names = [
                            "tempo", "energy", "valence", "loudness",
                            "danceability", "speechiness", "acousticness",
                            "instrumentalness", "liveness"
                        ]
                        
                        # Try different column name variations
                        feature_map = {
                            "tempo": ["tempo", "Tempo"],
                            "energy": ["energy", "Energy"],
                            "valence": ["valence", "Valence", "Positiveness"],
                            "loudness": ["loudness", "Loudness", "Loudness (dB)", "Loudness (db)"],
                            "danceability": ["danceability", "Danceability"],
                            "speechiness": ["speechiness", "Speechiness"],
                            "acousticness": ["acousticness", "Acousticness"],
                            "instrumentalness": ["instrumentalness", "Instrumentalness"],
                            "liveness": ["liveness", "Liveness"]
                        }
                        
                        features = {}
                        for feat, possible_cols in feature_map.items():
                            for col in possible_cols:
                                if col in song_row.index:
                                    val = song_row[col]
                                    if pd.notna(val):
                                        features[feat] = float(val)
                                        break
                        
                        if len(features) >= 3:  # At least some features found
                            print(f"Found song '{song_name}' in dataset")
                            return features
                
            except Exception as e:
                print(f"Error searching in {file_name}: {e}")
                continue
    
    return None

def find_lyrics_in_dataset(song_name, artist_name):
    """
    Try to find lyrics in dataset
    
    Returns:
        Lyrics text or None if not found
    """
    # Try files that might have lyrics
    for file_name in ["songs_mapped.csv", "songs_with_predictions.csv", "songs.csv"]:
        file_path = DATA_DIR / file_name if DATA_DIR.exists() else BASE / file_name
        if not file_path.exists():
            continue
            
        try:
            # Look for text/lyrics column
            df = pd.read_csv(file_path, nrows=50000)
            
            # Find text/lyrics column
            lyrics_col = None
            for col in ['text', 'lyrics', 'Lyrics', 'Text', 'song_text']:
                if col in df.columns:
                    lyrics_col = col
                    break
            
            if lyrics_col:
                # Find song column
                song_col = None
                for col in ['song', 'track_name', 'Song', 'Track Name']:
                    if col in df.columns:
                        song_col = col
                        break
                
                if song_col:
                    mask = df[song_col].str.lower().str.contains(song_name.lower(), na=False)
                    matches = df[mask]
                    if len(matches) > 0:
                        lyrics = matches.iloc[0][lyrics_col]
                        if pd.notna(lyrics) and str(lyrics).strip():
                            print(f"Found lyrics for '{song_name}' in dataset")
                            return str(lyrics)
        
        except Exception as e:
            print(f"Error searching lyrics in {file_name}: {e}")
            continue
    
    return None

if __name__ == '__main__':
    print("=" * 60)
    print("Spotify Song Mood Classifier API Server")
    print("=" * 60)
    print(f"Audio model loaded: {model_data is not None}")
    print(f"Lyrics classifier loaded: {lyrics_classifier is not None}")
    print("\nAPI Endpoints:")
    print("  GET  /api/health   - Health check")
    print("  GET  /api/stats    - Get statistics for charts")
    print("  GET  /api/dataset  - Get dataset distribution")
    print("  POST /api/predict  - Predict song mood")
    print("\nStarting server on http://localhost:8000")
    print("=" * 60)
    app.run(debug=True, port=8000, host='0.0.0.0')

