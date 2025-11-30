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
    return jsonify({
        "status": "ok", 
        "audio_model_loaded": model_data is not None,
        "lyrics_model_loaded": lyrics_classifier is not None
    })

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
                if audio_info:
                    confidence = float(audio_info["confidence"][0])
                    audio_result = {
                        "mood": str(audio_info["predictions"][0]),
                        "confidence": confidence,
                        "lowConfidence": confidence < AUDIO_LOW_CONF_THRESHOLD
                    }
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
                    lyrics_result = {
                        "mood": mood,
                        "confidence": float(confidence),
                        "lowConfidence": float(confidence) < LYRICS_LOW_CONF_THRESHOLD
                    }
            except Exception as e:
                print(f"Error getting lyrics prediction: {e}")
                # Don't fail if lyrics prediction fails, just skip it
        
        # Check if predictions agree
        agree = False
        if audio_result and lyrics_result:
            agree = audio_result["mood"] == lyrics_result["mood"]
        elif not lyrics_result:
            # If no lyrics prediction, just return audio
            agree = None
        
        # Build response
        response = {
            "song": song_name,
            "artist": artist_name,
            "audio": audio_result,
            "agree": agree
        }
        
        if lyrics_result:
            response["lyrics"] = lyrics_result
        else:
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

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Get aggregated statistics for model comparison charts
    
    Response:
    {
        "agreement": {
            "agree": int,
            "disagree": int,
            "agree_pct": float,
            "disagree_pct": float
        },
        "distribution": [
            {"mood": "happy", "audio": float, "lyrics": float},
            ...
        ],
        "confusion": [
            {"audio": "happy", "happy": int, "chill": int, "sad": int, "hyped": int},
            ...
        ],
        "lowConfidence": [
            {"mood": "happy", "audio": float, "lyrics": float},
            ...
        ],
        "confidenceDistribution": [
            {"range": "0-0.2", "audio": int, "lyrics": int},
            ...
        ]
    }
    """
    try:
        # Try to load songs_with_predictions.csv
        predictions_file = DATA_DIR / "songs_with_predictions.csv"
        if not predictions_file.exists():
            return jsonify({
                "error": "Predictions file not found. Please run run_lyrics_comparison.py first to generate predictions.",
                "file_path": str(predictions_file)
            }), 404
        
        df = pd.read_csv(predictions_file)
        
        # Validate required columns
        required_cols = ['audio_prediction', 'lyrics_prediction']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return jsonify({
                "error": f"Missing required columns: {missing_cols}",
                "available_columns": list(df.columns)
            }), 400
        
        # Filter out rows with missing predictions
        df_valid = df.dropna(subset=['audio_prediction', 'lyrics_prediction']).copy()
        
        if len(df_valid) == 0:
            return jsonify({
                "error": "No valid predictions found in dataset"
            }), 400
        
        # Normalize predictions to lowercase strings - handle numpy arrays and various types
        try:
            df_valid['audio_prediction'] = df_valid['audio_prediction'].astype(str).str.lower().str.strip()
            df_valid['lyrics_prediction'] = df_valid['lyrics_prediction'].astype(str).str.lower().str.strip()
        except Exception as e:
            print(f"Error normalizing predictions: {e}")
            return jsonify({
                "error": f"Failed to normalize predictions: {str(e)}"
            }), 500
        
        # Replace 'nan' strings and invalid values with actual NaN
        df_valid['audio_prediction'] = df_valid['audio_prediction'].replace(['nan', 'none', 'null', ''], pd.NA)
        df_valid['lyrics_prediction'] = df_valid['lyrics_prediction'].replace(['nan', 'none', 'null', ''], pd.NA)
        
        # Filter out invalid mood values
        valid_moods = ['happy', 'chill', 'sad', 'hyped']
        df_valid = df_valid[
            df_valid['audio_prediction'].isin(valid_moods) & 
            df_valid['lyrics_prediction'].isin(valid_moods)
        ].copy()
        
        # Filter again after normalization
        df_valid = df_valid.dropna(subset=['audio_prediction', 'lyrics_prediction'])
        
        if len(df_valid) == 0:
            return jsonify({
                "error": "No valid predictions after normalization and filtering",
                "hint": "Check that predictions are one of: happy, chill, sad, hyped"
            }), 400
        
        # 1. Calculate agreement
        agreement_mask = df_valid['audio_prediction'] == df_valid['lyrics_prediction']
        agreement_count = int(agreement_mask.sum())
        total_count = len(df_valid)
        if total_count > 0:
            agreement_pct = float((agreement_count / total_count) * 100)
            # Ensure percentage is valid (not NaN or Infinity)
            if not (0 <= agreement_pct <= 100) or not (agreement_pct == agreement_pct):  # NaN check
                agreement_pct = 0.0
        else:
            agreement_pct = 0.0
        
        # 2. Calculate distribution by mood
        valid_moods = ['happy', 'chill', 'sad', 'hyped']
        
        # Filter to only valid moods before calculating distribution
        audio_dist = df_valid[df_valid['audio_prediction'].isin(valid_moods)]['audio_prediction'].value_counts(normalize=True) * 100
        lyrics_dist = df_valid[df_valid['lyrics_prediction'].isin(valid_moods)]['lyrics_prediction'].value_counts(normalize=True) * 100
        
        distribution = []
        for mood in valid_moods:
            if mood in audio_dist.index:
                audio_pct = float(audio_dist.get(mood, 0))
                # Validate: not NaN, not Infinity, in valid range
                if not (audio_pct == audio_pct) or not (-1000 <= audio_pct <= 1000):  # NaN and range check
                    audio_pct = 0.0
            else:
                audio_pct = 0.0
            
            if mood in lyrics_dist.index:
                lyrics_pct = float(lyrics_dist.get(mood, 0))
                # Validate: not NaN, not Infinity, in valid range
                if not (lyrics_pct == lyrics_pct) or not (-1000 <= lyrics_pct <= 1000):  # NaN and range check
                    lyrics_pct = 0.0
            else:
                lyrics_pct = 0.0
            
            distribution.append({
                "mood": mood.capitalize(),
                "audio": max(0.0, min(100.0, audio_pct)),  # Clamp to 0-100
                "lyrics": max(0.0, min(100.0, lyrics_pct))  # Clamp to 0-100
            })
        
        # 3. Calculate confusion matrix
        confusion = []
        for audio_mood in valid_moods:
            audio_mask = df_valid['audio_prediction'] == audio_mood
            audio_subset = df_valid[audio_mask]
            
            if len(audio_subset) > 0:
                # Filter to only valid lyrics predictions
                lyrics_subset = audio_subset[audio_subset['lyrics_prediction'].isin(valid_moods)]
                lyrics_counts = lyrics_subset['lyrics_prediction'].value_counts()
                confusion.append({
                    "audio": audio_mood.capitalize(),
                    "happy": int(lyrics_counts.get('happy', 0)) if 'happy' in lyrics_counts.index else 0,
                    "chill": int(lyrics_counts.get('chill', 0)) if 'chill' in lyrics_counts.index else 0,
                    "sad": int(lyrics_counts.get('sad', 0)) if 'sad' in lyrics_counts.index else 0,
                    "hyped": int(lyrics_counts.get('hyped', 0)) if 'hyped' in lyrics_counts.index else 0
                })
            else:
                confusion.append({
                    "audio": audio_mood.capitalize(),
                    "happy": 0,
                    "chill": 0,
                    "sad": 0,
                    "hyped": 0
                })
        
        # 4. Calculate low confidence by mood
        low_confidence = []
        if 'audio_confidence' in df_valid.columns and 'lyrics_confidence' in df_valid.columns:
            # Convert confidence columns to numeric, handling any type issues
            df_conf = df_valid.copy()
            df_conf['audio_confidence'] = pd.to_numeric(df_conf['audio_confidence'], errors='coerce')
            df_conf['lyrics_confidence'] = pd.to_numeric(df_conf['lyrics_confidence'], errors='coerce')
            
            # Drop rows with invalid confidence values
            df_conf = df_conf.dropna(subset=['audio_confidence', 'lyrics_confidence']).copy()
            
            # Ensure confidence values are in valid range [0, 1]
            df_conf['audio_confidence'] = df_conf['audio_confidence'].clip(0, 1)
            df_conf['lyrics_confidence'] = df_conf['lyrics_confidence'].clip(0, 1)
            
            for mood in valid_moods:
                # Calculate audio low confidence for this mood
                audio_mask = (df_conf['audio_prediction'] == mood) & (df_conf['audio_confidence'].notna())
                audio_subset = df_conf[audio_mask]
                audio_total = len(audio_subset)
                if audio_total > 0:
                    audio_low = int((audio_subset['audio_confidence'] < AUDIO_LOW_CONF_THRESHOLD).sum())
                    audio_pct = float((audio_low / audio_total) * 100)
                    # Validate: not NaN, not Infinity
                    if not (audio_pct == audio_pct) or not (0 <= audio_pct <= 100):
                        audio_pct = 0.0
                else:
                    audio_pct = 0.0
                
                # Calculate lyrics low confidence for this mood
                lyrics_mask = (df_conf['lyrics_prediction'] == mood) & (df_conf['lyrics_confidence'].notna())
                lyrics_subset = df_conf[lyrics_mask]
                lyrics_total = len(lyrics_subset)
                if lyrics_total > 0:
                    lyrics_low = int((lyrics_subset['lyrics_confidence'] < LYRICS_LOW_CONF_THRESHOLD).sum())
                    lyrics_pct = float((lyrics_low / lyrics_total) * 100)
                    # Validate: not NaN, not Infinity
                    if not (lyrics_pct == lyrics_pct) or not (0 <= lyrics_pct <= 100):
                        lyrics_pct = 0.0
                else:
                    lyrics_pct = 0.0
                
                low_confidence.append({
                    "mood": mood.capitalize(),
                    "audio": float(audio_pct),
                    "lyrics": float(lyrics_pct)
                })
        else:
            # If confidence columns don't exist, return zeros
            for mood in valid_moods:
                low_confidence.append({
                    "mood": mood.capitalize(),
                    "audio": 0.0,
                    "lyrics": 0.0
                })
        
        # 5. Calculate confidence distribution
        confidence_distribution = []
        if 'audio_confidence' in df_valid.columns and 'lyrics_confidence' in df_valid.columns:
            # Convert confidence columns to numeric, handling any type issues
            df_conf = df_valid.copy()
            df_conf['audio_confidence'] = pd.to_numeric(df_conf['audio_confidence'], errors='coerce')
            df_conf['lyrics_confidence'] = pd.to_numeric(df_conf['lyrics_confidence'], errors='coerce')
            
            # Drop rows with invalid confidence values
            df_conf = df_conf.dropna(subset=['audio_confidence', 'lyrics_confidence']).copy()
            
            # Ensure confidence values are in valid range [0, 1]
            df_conf['audio_confidence'] = df_conf['audio_confidence'].clip(0, 1)
            df_conf['lyrics_confidence'] = df_conf['lyrics_confidence'].clip(0, 1)
            
            if len(df_conf) > 0:
                # Define bins and labels - use 1.01 to include 1.0 in last bin
                bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.01]
                labels = ["0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]
                
                try:
                    # Bin the confidence values
                    audio_binned = pd.cut(df_conf['audio_confidence'], bins=bins, labels=labels, include_lowest=True, right=False)
                    lyrics_binned = pd.cut(df_conf['lyrics_confidence'], bins=bins, labels=labels, include_lowest=True, right=False)
                    
                    # Count values in each bin
                    audio_counts = audio_binned.value_counts().sort_index()
                    lyrics_counts = lyrics_binned.value_counts().sort_index()
                    
                    for label in labels:
                        audio_count = int(audio_counts.get(label, 0)) if label in audio_counts.index else 0
                        lyrics_count = int(lyrics_counts.get(label, 0)) if label in lyrics_counts.index else 0
                        # Ensure non-negative integers
                        audio_count = max(0, audio_count) if not (audio_count != audio_count) else 0  # NaN check
                        lyrics_count = max(0, lyrics_count) if not (lyrics_count != lyrics_count) else 0  # NaN check
                        confidence_distribution.append({
                            "range": str(label),
                            "audio": audio_count,
                            "lyrics": lyrics_count
                        })
                except Exception as e:
                    print(f"Error binning confidence values: {e}")
                    # Return zeros if binning fails
                    for label in labels:
                        confidence_distribution.append({
                            "range": label,
                            "audio": 0,
                            "lyrics": 0
                        })
            else:
                # No valid confidence data
                for label in ["0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]:
                    confidence_distribution.append({
                        "range": label,
                        "audio": 0,
                        "lyrics": 0
                    })
        else:
            # If confidence columns don't exist, return zeros
            for label in ["0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]:
                confidence_distribution.append({
                    "range": label,
                    "audio": 0,
                    "lyrics": 0
                })
        
        # Ensure all arrays are non-empty and valid
        if not distribution:
            distribution = [{"mood": mood.capitalize(), "audio": 0.0, "lyrics": 0.0} for mood in valid_moods]
        if not confusion:
            confusion = [{"audio": mood.capitalize(), "happy": 0, "chill": 0, "sad": 0, "hyped": 0} for mood in valid_moods]
        if not low_confidence:
            low_confidence = [{"mood": mood.capitalize(), "audio": 0.0, "lyrics": 0.0} for mood in valid_moods]
        if not confidence_distribution:
            confidence_distribution = [{"range": label, "audio": 0, "lyrics": 0} for label in ["0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]]
        
        # Ensure disagree_pct is valid
        disagree_pct = float(100 - agreement_pct)
        if not (disagree_pct == disagree_pct) or not (0 <= disagree_pct <= 100):  # NaN and range check
            disagree_pct = max(0.0, min(100.0, 100 - agreement_pct))
        
        return jsonify({
            "agreement": {
                "agree": int(agreement_count),
                "disagree": int(max(0, total_count - agreement_count)),
                "agree_pct": float(max(0.0, min(100.0, agreement_pct))),
                "disagree_pct": float(disagree_pct)
            },
            "distribution": distribution,
            "confusion": confusion,
            "lowConfidence": low_confidence,
            "confidenceDistribution": confidence_distribution
        })
        
    except Exception as e:
        print(f"Error in /api/stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/dataset', methods=['GET'])
def get_dataset():
    """
    Get dataset distribution statistics
    
    Response:
    {
        "distribution": [
            {"mood": "happy", "count": int, "percentage": float},
            ...
        ],
        "total": int
    }
    """
    try:
        # Try to load dataset with mood labels
        dataset_files = [
            DATA_DIR / "songs_mapped_20k_balanced.csv",
            DATA_DIR / "songs_mapped.csv",
            DATA_DIR / "songs_with_predictions.csv"
        ]
        
        df = None
        for file_path in dataset_files:
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    if 'mood' in df.columns:
                        break
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    continue
        
        if df is None or 'mood' not in df.columns:
            return jsonify({
                "error": "Dataset with mood labels not found",
                "tried_files": [str(f) for f in dataset_files]
            }), 404
        
        # Filter valid moods and normalize
        valid_moods = ['happy', 'chill', 'sad', 'hyped']
        df_valid = df.dropna(subset=['mood']).copy()
        df_valid['mood'] = df_valid['mood'].astype(str).str.lower().str.strip()
        df_valid = df_valid[df_valid['mood'].isin(valid_moods)]
        
        if len(df_valid) == 0:
            return jsonify({
                "error": "No valid mood labels found in dataset"
            }), 400
        
        # Calculate distribution
        mood_counts = df_valid['mood'].value_counts()
        total = len(df_valid)
        
        distribution = []
        for mood in valid_moods:
            count = int(mood_counts.get(mood, 0))
            percentage = (count / total * 100) if total > 0 else 0
            distribution.append({
                "mood": mood.capitalize(),
                "count": count,
                "percentage": float(percentage)
            })
        
        return jsonify({
            "distribution": distribution,
            "total": int(total)
        })
        
    except Exception as e:
        print(f"Error in /api/dataset: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("Spotify Song Mood Classifier API Server")
    print("=" * 60)
    print(f"Audio model loaded: {model_data is not None}")
    print(f"Lyrics classifier loaded: {lyrics_classifier is not None}")
    print("\nAPI Endpoints:")
    print("  GET  /api/health   - Health check")
    print("  POST /api/predict  - Predict song mood")
    print("  GET  /api/stats    - Get model comparison statistics")
    print("  GET  /api/dataset   - Get dataset distribution")
    print("\nStarting server on http://localhost:8000")
    print("=" * 60)
    app.run(debug=True, port=8000, host='0.0.0.0')

