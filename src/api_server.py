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

if __name__ == '__main__':
    print("=" * 60)
    print("Spotify Song Mood Classifier API Server")
    print("=" * 60)
    print(f"Audio model loaded: {model_data is not None}")
    print(f"Lyrics classifier loaded: {lyrics_classifier is not None}")
    print("\nAPI Endpoints:")
    print("  GET  /api/health  - Health check")
    print("  POST /api/predict - Predict song mood")
    print("\nStarting server on http://localhost:8000")
    print("=" * 60)
    app.run(debug=True, port=8000, host='0.0.0.0')

