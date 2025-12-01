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
    print("Warning: openai package not installed")


class LyricsClassifier:
    def __init__(self, api_key=None):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package is required")

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
    
        if not lyrics or pd.isna(lyrics) or str(lyrics).strip() == '':
            return None, 0.0
        
        # Create prompt for OpenAI
        prompt = self._create_prompt(lyrics, song_name, artist)
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  
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
                temperature=0.3, 
                max_tokens=10    
            )
            
            # Get the prediction
            predicted_mood = response.choices[0].message.content.strip().lower()
            
            # Clean up the prediction (remove punctuation, extra words)
            predicted_mood = predicted_mood.replace('.', '').replace(',', '').strip()
            
            # Validate that it's one of our moods
            if predicted_mood not in self.mood_labels:
                for mood in self.mood_labels:
                    if mood in predicted_mood:
                        predicted_mood = mood
                        break
                else:
                    predicted_mood = 'chill'
            
            self.api_calls += 1
            
            # Simple confidence
            confidence = 0.8 if predicted_mood in self.mood_labels else 0.5
            
            return predicted_mood, confidence
            
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None, 0.0
    
    def _create_prompt(self, lyrics, song_name=None, artist=None):
        prompt = "Classify this song's mood based on its lyrics.\n\n"
        
        if song_name and artist:
            prompt += f"Song: {song_name} by {artist}\n\n"
        elif song_name:
            prompt += f"Song: {song_name}\n\n"
        
        prompt += "Lyrics:\n"
        prompt += str(lyrics)[:2000] 
        prompt += "\n\n"
        prompt += "Choose ONE mood: happy, chill, sad, or hyped.\n"
        prompt += "Respond with ONLY the mood word (lowercase)."
        
        return prompt
    
    def classify_dataset(self, df, lyrics_column='text', song_column='track_name', 
                        artist_column='artists', max_songs=None, delay=1):

        result_df = df.copy()
        
        if lyrics_column not in df.columns:
            raise ValueError(f"Lyrics column '{lyrics_column}' not found in dataset.")
        

        if max_songs:
            df_to_process = df.head(max_songs).copy()
        else:
            df_to_process = df.copy()
        
        predictions = []
        confidences = []
        
        print(f"Classifying {len(df_to_process)} songs using OpenAI API...")
        
        for idx, row in df_to_process.iterrows():
            lyrics = row.get(lyrics_column, '')
            song_name = row.get(song_column, None) if song_column in df.columns else None
            artist = row.get(artist_column, None) if artist_column in df.columns else None
            
            # Classify this song
            mood, confidence = self.classify_lyrics(lyrics, song_name, artist)
            
            predictions.append(mood)
            confidences.append(confidence)
            
            if (idx + 1) % 10 == 0:
                print(f"Processed {idx + 1}/{len(df_to_process)} songs...")
            
            if delay > 0 and idx < len(df_to_process) - 1:
                time.sleep(delay)

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

    print("Lyrics-based Mood Classifier")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set.")
        print("Please set it before running this script.")
        return

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
    
if __name__ == "__main__":
    main()

