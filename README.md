# Spotify Song Mood Classifier

A machine learning system for classifying songs into mood categories (happy, chill, sad, hyped) using audio features and lyrics analysis.

## Project Overview

This project implements a system that:
- Classifies songs into mood categories using audio features (trained model)
- Analyzes lyrics using VADER sentiment analysis
- Compares audio and lyrics predictions
- Generates predictions and statistics from datasets

## Prerequisites

- Python 3.8 or higher
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Spotify-Song-Classifier
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Required Files

Before running the system, ensure you have:

1. **Dataset**: `data/processed/songs_mapped_20k_balanced.csv` (or similar)
   - Must contain columns: `mood`, and optionally `text` or `lyrics` for lyrics analysis

2. **Trained Model**: `models/new_song_mood_model.joblib`
   - Audio classification model trained on audio features

## Quick Start

### Generate Predictions File

The main script runs audio and lyrics predictions on your dataset:

```bash
python src/run_lyrics_comparison.py
```

This script:
- Loads the dataset from `data/processed/songs_mapped_20k_balanced.csv`
- Runs audio predictions using the trained model
- Runs lyrics predictions using VADER sentiment analysis
- Saves results to `data/processed/songs_with_predictions.csv`

**Prerequisites**:
- Dataset file must exist at `data/processed/songs_mapped_20k_balanced.csv`
- Model file must exist at `models/new_song_mood_model.joblib`
- Dataset must have a lyrics column (`text`, `lyrics`, `Lyrics`, `Text`, or `song_text`)

## Using the Classifiers Directly in Python

### Audio Classification

```python
from src.run_lyrics_comparison import load_audio_model, get_audio_predictions
import pandas as pd
from pathlib import Path

# Load the model
model_path = Path("models/new_song_mood_model.joblib")
model_data = load_audio_model(model_path)

# Prepare your data (must have the required audio features)
df = pd.DataFrame([{
    'tempo': 120.0,
    'energy': 0.8,
    'valence': 0.7,
    'loudness': -5.0,
    'danceability': 0.6,
    'speechiness': 0.1,
    'acousticness': 0.2,
    'instrumentalness': 0.0,
    'liveness': 0.1
}])

# Get predictions
audio_results = get_audio_predictions(df, model_data)
print(f"Mood: {audio_results['predictions'][0]}")
print(f"Confidence: {audio_results['confidence'][0]:.2f}")
```

### Lyrics Classification

```python
from src.lyrics_classifier_free import FreeLyricsClassifier

# Initialize classifier
classifier = FreeLyricsClassifier()

# Classify a single song's lyrics
mood, confidence = classifier.classify_lyrics(
    lyrics="I'm feeling good, life is great!",
    song_name="Happy Song",
    artist_name="Artist"
)

print(f"Mood: {mood}")
print(f"Confidence: {confidence:.2f}")
```

### Classify a Dataset

```python
from src.lyrics_classifier_free import FreeLyricsClassifier
import pandas as pd

# Load your dataset
df = pd.read_csv("data/processed/songs_mapped_20k_balanced.csv")

# Initialize classifier
classifier = FreeLyricsClassifier()

# Classify all songs in the dataset
df_with_predictions = classifier.classify_dataset(
    df,
    lyrics_column='text',  # or 'lyrics', 'Lyrics', etc.
    song_column='track_name',
    artist_column='artists',
    max_songs=100  # or None for all songs
)

# Results are in df_with_predictions['lyrics_prediction'] and df_with_predictions['lyrics_confidence']
```

## Python Scripts

### Main Scripts

1. **`src/run_lyrics_comparison.py`** - Main script to generate predictions
   - Runs both audio and lyrics predictions
   - Saves results to CSV
   - Generates comparison statistics

2. **`src/train_audio_model.py`** - Train a new audio classification model

3. **`src/train_lyrics_full.py`** - Train a lyrics classification model (if using trained model instead of VADER)

### Utility Scripts

- **`src/demo.py`** - Basic demo with sample songs
- **`src/demo_confident.py`** - Demo with confidence analysis
- **`src/test_free_lyrics.py`** - Test the free lyrics classifier
- **`src/compare_audio_lyrics.py`** - Generate comparison visualizations
- **`src/enhanced_visualizations.py`** - Various visualization functions

## Project Structure

```
Spotify-Song-Classifier/
├── src/
│   ├── run_lyrics_comparison.py      # Main script that generates predictions
│   ├── train_audio_model.py          # Train audio model
│   ├── train_lyrics_full.py          # Train lyrics model
│   ├── lyrics_classifier_free.py     # VADER-based lyrics classifier
│   ├── compare_audio_lyrics.py       # Comparison analysis
│   └── ...                          
├── data/
│   └── processed/
│       ├── songs_mapped_20k_balanced.csv  # Input dataset
│       └── songs_with_predictions.csv     # Generated predictions
├── models/
│   └── new_song_mood_model.joblib        # Trained audio model
├── requirements.txt                       #  dependencies
└── README.md                             
```


## Configuration

### File Paths

Default paths (can be modified in scripts):

**Dataset**: `data/processed/songs_mapped_20k_balanced.csv`
- The script looks for this specific file
- If you have a different filename, update `DATASET_PATH` in `src/run_lyrics_comparison.py`

**Model**: `models/new_song_mood_model.joblib`
- The script looks for this specific file
- If you have a different filename, update `MODEL_PATH` in `src/run_lyrics_comparison.py`

**Output**: `data/processed/songs_with_predictions.csv`
- Generated predictions are saved here

### Thresholds

Default confidence thresholds:
- Audio low confidence: < 0.35
- Lyrics low confidence: < 0.6

These are defined in the scripts and can be modified.

## Troubleshooting

### Model Not Loading

- Check that `models/new_song_mood_model.joblib` exists
- Verify the model file is not corrupted
- Ensure you have the correct model file format

### Dataset Issues

1. **File not found**:
   - Verify dataset exists in `data/processed/`
   - Check file name matches expected name
   - Update `DATASET_PATH` in the script if needed

2. **Missing columns**:
   - Ensure dataset has required audio features (tempo, energy, valence, etc.)
   - For lyrics analysis, ensure dataset has a lyrics column (`text`, `lyrics`, etc.)

3. **Lyrics column not found**:
   - The script tries these column names in order: `text`, `lyrics`, `Lyrics`, `Text`, `song_text`
   - Check available columns: 
     ```python
     import pandas as pd
     df = pd.read_csv('data/processed/songs_mapped_20k_balanced.csv', nrows=1)
     print(list(df.columns))
     ```

### Prediction Issues

1. **Missing audio features**:
   - Ensure your data has all required features
   - Missing features will be filled with 0, which may affect accuracy

2. **Lyrics prediction unavailable**:
   - Check that lyrics column exists and has data
   - Some songs may not have lyrics available

## Example: Complete Workflow

```python
from src.run_lyrics_comparison import load_audio_model, get_audio_predictions
from src.lyrics_classifier_free import FreeLyricsClassifier
import pandas as pd

# 1. Load dataset
df = pd.read_csv("data/processed/songs_mapped_20k_balanced.csv", nrows=100)

# 2. Get audio predictions
model_data = load_audio_model(Path("models/new_song_mood_model.joblib"))
audio_results = get_audio_predictions(df, model_data)
df['audio_prediction'] = audio_results['predictions']
df['audio_confidence'] = audio_results['confidence']

# 3. Get lyrics predictions
classifier = FreeLyricsClassifier()
df = classifier.classify_dataset(
    df,
    lyrics_column='text',
    song_column='track_name',
    artist_column='artists'
)

# 4. Compare results
df['agree'] = df['audio_prediction'] == df['lyrics_prediction']
agreement_rate = df['agree'].mean() * 100
print(f"Agreement rate: {agreement_rate:.1f}%")

# 5. Save results
df.to_csv("my_predictions.csv", index=False)
```

## Dependencies

Key dependencies (see `requirements.txt` for full list):
- pandas - Data manipulation
- numpy - Numerical operations
- scikit-learn - Machine learning
- joblib - Model serialization
- vaderSentiment - Lyrics sentiment analysis
- matplotlib, seaborn - Visualizations (optional)
