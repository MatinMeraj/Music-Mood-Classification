"""
Lyrics-based Mood Classifier using OpenAI API
Simple and clear implementation for Milestone 2
"""

import os
import pandas as pd
from pathlib import Path
import time

# OpenAI API setup
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai package not installed. Run: pip install openai")


class LyricsClassifier:
    """
    Simple lyrics-based mood classifier using OpenAI API.
    Classifies songs into: happy, chill, sad, hyped
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the lyrics classifier.
        
        Args:
            api_key: Your OpenAI API key. If None, will look for OPENAI_API_KEY environment variable.
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package is required. Install it with: pip install openai")
        
        # Get API key from parameter or environment variable
        if api_key is None:
            api_key = os.getenv('OPENAI_API_KEY')
        
        if api_key is None:
            raise ValueError(
                "OpenAI API key not found. "
                "Please set OPENAI_API_KEY environment variable or pass api_key parameter."
            )
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key)
        self.mood_labels = ['happy', 'chill', 'sad', 'hyped']
        
        # Count API calls (for monitoring)
        self.api_calls = 0
    
    def classify_lyrics(self, lyrics, song_name=None, artist=None):
        """
        Classify a song's mood based on its lyrics using OpenAI API.
        
        Args:
            lyrics: The song lyrics (text string)
            song_name: Optional song name (for better context)
            artist: Optional artist name (for better context)
        
        Returns:
            predicted_mood: One of ['happy', 'chill', 'sad', 'hyped']
            confidence: A simple confidence score (0-1)
        """
        if not lyrics or pd.isna(lyrics) or str(lyrics).strip() == '':
            return None, 0.0
        
        # Create prompt for OpenAI
        prompt = self._create_prompt(lyrics, song_name, artist)
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using cheaper model for testing
                messages=[
                    {
                        "role": "system",
                        "content": "You are a music mood classifier. Classify songs into one of four moods: happy, chill, sad, hyped. Only respond with one word: the mood."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature = more consistent
                max_tokens=10     # We only need one word
            )
            
            # Get the prediction
            predicted_mood = response.choices[0].message.content.strip().lower()
            
            # Clean up the prediction (remove punctuation, extra words)
            predicted_mood = predicted_mood.replace('.', '').replace(',', '').strip()
            
            # Validate that it's one of our moods
            if predicted_mood not in self.mood_labels:
                # Try to find mood in the response
                for mood in self.mood_labels:
                    if mood in predicted_mood:
                        predicted_mood = mood
                        break
                else:
                    # Default to 'chill' if we can't parse it
                    predicted_mood = 'chill'
            
            self.api_calls += 1
            
            # Simple confidence (we'll improve this later)
            confidence = 0.8 if predicted_mood in self.mood_labels else 0.5
            
            return predicted_mood, confidence
            
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None, 0.0
    
    def _create_prompt(self, lyrics, song_name=None, artist=None):
        """
        Create a prompt for OpenAI API.
        Keep it simple and clear.
        """
        prompt = "Classify this song's mood based on its lyrics.\n\n"
        
        if song_name and artist:
            prompt += f"Song: {song_name} by {artist}\n\n"
        elif song_name:
            prompt += f"Song: {song_name}\n\n"
        
        prompt += "Lyrics:\n"
        prompt += str(lyrics)[:2000]  # Limit to 2000 characters to save tokens
        prompt += "\n\n"
        prompt += "Choose ONE mood: happy, chill, sad, or hyped.\n"
        prompt += "Respond with ONLY the mood word (lowercase)."
        
        return prompt
    
    def classify_dataset(self, df, lyrics_column='text', song_column='track_name', 
                        artist_column='artists', max_songs=None, delay=1):
        """
        Classify multiple songs from a dataset.
        
        Args:
            df: DataFrame with songs and lyrics
            lyrics_column: Name of column with lyrics
            song_column: Name of column with song names
            artist_column: Name of column with artist names
            max_songs: Maximum number of songs to classify (None = all)
            delay: Delay between API calls in seconds (to avoid rate limits)
        
        Returns:
            DataFrame with predictions added as 'lyrics_prediction' column
        """
        # Make a copy to avoid modifying original
        result_df = df.copy()
        
        # Check if lyrics column exists
        if lyrics_column not in df.columns:
            raise ValueError(f"Lyrics column '{lyrics_column}' not found in dataset.")
        
        # Limit number of songs if specified
        if max_songs:
            df_to_process = df.head(max_songs).copy()
        else:
            df_to_process = df.copy()
        
        # List to store predictions
        predictions = []
        confidences = []
        
        print(f"Classifying {len(df_to_process)} songs using OpenAI API...")
        print("This may take a while. Please be patient.\n")
        
        for idx, row in df_to_process.iterrows():
            lyrics = row.get(lyrics_column, '')
            song_name = row.get(song_column, None) if song_column in df.columns else None
            artist = row.get(artist_column, None) if artist_column in df.columns else None
            
            # Classify this song
            mood, confidence = self.classify_lyrics(lyrics, song_name, artist)
            
            predictions.append(mood)
            confidences.append(confidence)
            
            # Print progress
            if (idx + 1) % 10 == 0:
                print(f"Processed {idx + 1}/{len(df_to_process)} songs...")
            
            # Delay between API calls to avoid rate limits
            if delay > 0 and idx < len(df_to_process) - 1:
                time.sleep(delay)
        
        # Add predictions to result dataframe
        result_df['lyrics_prediction'] = None
        result_df['lyrics_confidence'] = 0.0
        
        if max_songs:
            result_df.loc[df_to_process.index, 'lyrics_prediction'] = predictions
            result_df.loc[df_to_process.index, 'lyrics_confidence'] = confidences
        else:
            result_df['lyrics_prediction'] = predictions
            result_df['lyrics_confidence'] = confidences
        
        print(f"\nFinished! Classified {len(df_to_process)} songs.")
        print(f"Total API calls: {self.api_calls}")
        
        return result_df


def main():
    """
    Simple example of how to use the lyrics classifier.
    """
    print("=" * 60)
    print("Lyrics-based Mood Classifier")
    print("=" * 60)
    print()
    
    # Check if API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set.")
        print("Please set it before running this script.")
        print("Example: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Initialize classifier
    print("Initializing lyrics classifier...")
    classifier = LyricsClassifier(api_key=api_key)
    
    # Test with a simple example
    print("\nTesting with a sample song...")
    test_lyrics = """
    I'm walking on sunshine, whoa-oh
    And don't it feel good
    I'm walking on sunshine, whoa-oh
    And don't it feel good
    """
    
    mood, confidence = classifier.classify_lyrics(
        test_lyrics,
        song_name="Walking on Sunshine",
        artist="Katrina and the Waves"
    )
    
    print(f"Predicted mood: {mood}")
    print(f"Confidence: {confidence:.2f}")
    print()
    
    # Example: Load dataset and classify (uncomment to use)
    """
    dataset_path = Path("data/processed/songs_mapped.csv")
    if dataset_path.exists():
        print(f"Loading dataset from {dataset_path}...")
        df = pd.read_csv(dataset_path)
        
        # Classify first 10 songs as a test
        print("Classifying first 10 songs...")
        df_with_predictions = classifier.classify_dataset(
            df,
            lyrics_column='text',  # Adjust based on your dataset
            max_songs=10,
            delay=1  # 1 second delay between API calls
        )
        
        # Save results
        output_path = Path("data/processed/songs_with_lyrics_predictions.csv")
        df_with_predictions.to_csv(output_path, index=False)
        print(f"Saved results to {output_path}")
    else:
        print(f"Dataset not found at {dataset_path}")
    """


if __name__ == "__main__":
    main()

