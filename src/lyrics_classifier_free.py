
import pandas as pd
from pathlib import Path
import os

# Try to import VADER
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("VADER not installed. Run: pip install vaderSentiment")


class FreeLyricsClassifier:

    
    def __init__(self):
        if not VADER_AVAILABLE:
            raise ImportError("VADER not installed. Run: pip install vaderSentiment")
        
        self.analyzer = SentimentIntensityAnalyzer()
        self.mood_labels = ['happy', 'chill', 'sad', 'hyped']
        self.api_calls = 0  # Keep for compatibility
    
    def classify_lyrics(self, lyrics, song_name=None, artist=None):
        
        if not lyrics or pd.isna(lyrics) or str(lyrics).strip() == '':
            #return None, 0.0
            return 'chill', 0.1  
        
        # Get sentiment scores
        scores = self.analyzer.polarity_scores(str(lyrics))
        
        # Compound score: -1 (very negative) to +1 (very positive)
        compound = scores['compound']
        
        # Map to moods based on sentiment and intensity
        if compound > 0.5:
            # Very positive = happy
            mood = 'happy'
            confidence = compound
        elif compound > 0.1:
            # Slightly positive = chill
            mood = 'chill'
            # Boost confidence
            confidence = 0.5 + (compound - 0.1) * 0.625  
        elif compound < -0.5:
            # Very negative = sad
            mood = 'sad'
            confidence = abs(compound)
        elif compound < -0.1:
            # Slightly negative = could be sad or chill
            if abs(compound) > 0.3:
                mood = 'sad'
                confidence = abs(compound)
            else:
                mood = 'chill'
                # Boost confidence for near-neutral chill
                confidence = 0.55 + (0.3 - abs(compound)) * 0.5  
        else:
            # Neutral = chill
            mood = 'chill'
            confidence = 0.65  # Neutral songs are confidently "chill"
        
        # Check for "hyped" keywords    
        lyrics_lower = str(lyrics).lower()
        hyped_keywords = ['party', 'dance', 'energy', 'fire', 'wild', 'crazy', 'lit', 
                         'pump', 'beat', 'bass', 'drop', 'turnt', 'hype']
        if any(keyword in lyrics_lower for keyword in hyped_keywords):
            if compound > 0.2:  # Positive + energy = hyped
                mood = 'hyped'
                confidence = min(0.9, abs(compound) + 0.2)
        
        # Ensure confidence is in valid range [0, 1] and not NaN
        confidence = max(0.0, min(1.0, float(confidence)))
        if confidence != confidence:  # NaN check
            confidence = 0.1  # Default low confidence
        
        # Ensure mood is valid
        if mood not in self.mood_labels:
            mood = 'chill'  # Default mood
        
        self.api_calls += 1
        return mood, confidence
    
    def classify_dataset(self, df, lyrics_column='text', song_column='track_name', 
                        artist_column='artists', max_songs=None, delay=0):
        
        result_df = df.copy()
        
        if lyrics_column not in df.columns:
            raise ValueError(f"Lyrics column '{lyrics_column}' not found")
        
        if max_songs:
            df_to_process = df.head(max_songs).copy()
        else:
            df_to_process = df.copy()
        
        predictions = []
        confidences = []
        
        print(f"Classifying {len(df_to_process)} songs using FREE VADER...")
        print("(No API cost, runs locally!)")
        print()
        
        for idx, row in df_to_process.iterrows():
            lyrics = row.get(lyrics_column, '')
            song_name = row.get(song_column, None) if song_column in df.columns else None
            artist = row.get(artist_column, None) if artist_column in df.columns else None
            
            mood, confidence = self.classify_lyrics(lyrics, song_name, artist)
            
            predictions.append(mood)
            confidences.append(confidence)
            
            if (idx + 1) % 100 == 0:
                print(f"Processed {idx + 1}/{len(df_to_process)} songs...")
        
        # Add predictions
        result_df['lyrics_prediction'] = None
        result_df['lyrics_confidence'] = 0.0
        
        if max_songs:
            result_df.loc[df_to_process.index, 'lyrics_prediction'] = predictions
            result_df.loc[df_to_process.index, 'lyrics_confidence'] = confidences
        else:
            result_df['lyrics_prediction'] = predictions
            result_df['lyrics_confidence'] = confidences
        
        print(f"\nFinished! Classified {len(df_to_process)} songs.")
        print(f"Total classifications: {self.api_calls}")
  
        
        return result_df


def main():

    print(" Lyrics Classifier VADER")

    
    if not VADER_AVAILABLE:
        print("VADER not installed!")
        return
    
    # Initialize classifier
    classifier = FreeLyricsClassifier()
    
    # Test with sample lyrics
    test_cases = [
        ("I'm walking on sunshine, whoa-oh\nAnd don't it feel good", "happy"),
        ("Raindrops keep falling on my head\nAnd just like the guy whose feet are too big", "sad"),
        ("Chill out, relax, take it easy\nEverything's gonna be alright", "chill"),
        ("Let's party all night, turn up the bass\nEverybody dance, feel the energy", "hyped"),
    ]
    
    print("Testing with sample lyrics:")
    print()
    for lyrics, expected in test_cases:
        mood, confidence = classifier.classify_lyrics(lyrics)
        match = "good" if mood == expected else "bad"
        print(f"{match} Expected: {expected:6s} | Got: {mood:6s} | Confidence: {confidence:.2f}")
    



if __name__ == "__main__":
    main()

