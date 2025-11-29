
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class MoodClassifier:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.mood_labels = ['happy', 'chill', 'sad', 'hyped']
        
    def load_music_dataset(self):
        print("Loading music dataset...")
        
        try:
            # Try to load the real dataset
            df = pd.read_csv('music_dataset.csv')
            print(f"Loaded {len(df)} songs from dataset")
            print(f"Mood distribution:")
            print(df['mood'].value_counts())
            print(f"Genre distribution:")
            print(df['genre'].value_counts())
            return df
            
        except FileNotFoundError:
            print("Dataset not found. Creating fallback dataset...")
            return self.create_fallback_dataset()
    
    def create_fallback_dataset(self):
        print("Creating fallback dataset...")
        np.random.seed(42)
        
        data = []
        for mood in self.mood_labels:
            n_mood_samples = 200
            
            if mood == 'happy':
                tempo = np.random.normal(125, 30, n_mood_samples)
                energy = np.random.beta(4, 3, n_mood_samples)
                valence = np.random.beta(5, 3, n_mood_samples)
                loudness = np.random.normal(-8, 5, n_mood_samples)
                
            elif mood == 'chill':
                tempo = np.random.normal(95, 25, n_mood_samples)
                energy = np.random.beta(3, 4, n_mood_samples)
                valence = np.random.beta(4, 4, n_mood_samples)
                loudness = np.random.normal(-11, 4, n_mood_samples)
                
            elif mood == 'sad':
                tempo = np.random.normal(85, 20, n_mood_samples)
                energy = np.random.beta(3, 5, n_mood_samples)
                valence = np.random.beta(2, 5, n_mood_samples)
                loudness = np.random.normal(-13, 3, n_mood_samples)
                
            else:  # hyped
                tempo = np.random.normal(145, 35, n_mood_samples)
                energy = np.random.beta(5, 3, n_mood_samples)
                valence = np.random.beta(5, 3, n_mood_samples)
                loudness = np.random.normal(-6, 3, n_mood_samples)
            
            for i in range(n_mood_samples):
                data.append({
                    'track_id': f"fallback_{mood}_{i}",
                    'track_name': f"Fallback {mood.title()} Song {i}",
                    'artists': f"Fallback Artist {i}",
                    'tempo': max(50, min(200, tempo[i])),
                    'energy': max(0, min(1, energy[i])),
                    'valence': max(0, min(1, valence[i])),
                    'loudness': max(-60, min(0, loudness[i])),
                    'danceability': np.random.beta(3, 3),
                    'speechiness': np.random.beta(2, 8),
                    'acousticness': np.random.beta(2, 8),
                    'instrumentalness': np.random.beta(1, 9),
                    'liveness': np.random.beta(2, 8),
                    'mood': mood
                })
        
        df = pd.DataFrame(data)
        print(f"Created fallback dataset with {len(df)} songs")
        return df
    
    def train_models(self, df):
        print("\nTraining models on dataset...")

        features = ['tempo', 'energy', 'valence', 'loudness', 'danceability', 
                   'speechiness', 'acousticness', 'instrumentalness', 'liveness']
        
        X = df[features]
        y = df['mood']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train multiple models
        models = {
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
            'KNN': KNeighborsClassifier(n_neighbors=5)
        }
        
        results = {}
        best_model = None
        best_score = 0
        
        for name, model in models.items():
            # Cross validation
            scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
            mean_score = scores.mean()
            std_score = scores.std()
            
            # Train on full training set
            model.fit(X_train_scaled, y_train)
            
            # Test performance
            y_pred = model.predict(X_test_scaled)
            test_accuracy = accuracy_score(y_test, y_pred)
            
            results[name] = {
                'cv_score': mean_score,
                'cv_std': std_score,
                'test_accuracy': test_accuracy,
                'model': model
            }
            
            print(f"{name:20s}: CV={mean_score:.3f}±{std_score:.3f}, Test={test_accuracy:.3f}")
            
            if mean_score > best_score:
                best_score = mean_score
                best_model = model
        
        # Select best model
        self.model = best_model
        best_name = max(results.keys(), key=lambda k: results[k]['cv_score'])
        
        print(f"\nBest Model: {best_name}")
        print(f"CV Score: {results[best_name]['cv_score']:.3f} ± {results[best_name]['cv_std']:.3f}")
        print(f"Test Accuracy: {results[best_name]['test_accuracy']:.3f}")
        
        # Detailed evaluation
        y_pred = best_model.predict(X_test_scaled)
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=self.mood_labels))
        
        return results, X_test, y_test, y_pred
    
    def create_visualizations(self, df, X_test, y_test, y_pred):
        print("\nCreating visualizations...")
        
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Song Mood Classification Analysis', fontsize=16, fontweight='bold')
        
        # Mood distribution
        mood_counts = df['mood'].value_counts()
        axes[0,0].bar(mood_counts.index, mood_counts.values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        axes[0,0].set_title('Mood Distribution in Dataset')
        axes[0,0].set_xlabel('Mood')
        axes[0,0].set_ylabel('Number of Songs')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # Tempo vs Energy by mood
        for mood in self.mood_labels:
            mood_data = df[df['mood'] == mood]
            axes[0,1].scatter(mood_data['tempo'], mood_data['energy'], 
                             label=mood, alpha=0.6, s=30)
        axes[0,1].set_xlabel('Tempo (BPM)')
        axes[0,1].set_ylabel('Energy')
        axes[0,1].set_title('Tempo vs Energy by Mood')
        axes[0,1].legend()
        axes[0,1].grid(True, alpha=0.3)
        
        # Valence vs Loudness by mood
        for mood in self.mood_labels:
            mood_data = df[df['mood'] == mood]
            axes[0,2].scatter(mood_data['valence'], mood_data['loudness'], 
                             label=mood, alpha=0.6, s=30)
        axes[0,2].set_xlabel('Valence')
        axes[0,2].set_ylabel('Loudness (dB)')
        axes[0,2].set_title('Valence vs Loudness by Mood')
        axes[0,2].legend()
        axes[0,2].grid(True, alpha=0.3)
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred, labels=self.mood_labels)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=self.mood_labels, yticklabels=self.mood_labels, ax=axes[1,0])
        axes[1,0].set_title('Confusion Matrix')
        axes[1,0].set_xlabel('Predicted')
        axes[1,0].set_ylabel('Actual')
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            feature_names = ['tempo', 'energy', 'valence', 'loudness', 'danceability', 
                           'speechiness', 'acousticness', 'instrumentalness', 'liveness']
            importance = self.model.feature_importances_
            feature_importance = pd.DataFrame({
                'feature': feature_names,
                'importance': importance
            }).sort_values('importance', ascending=True)
            
            axes[1,1].barh(feature_importance['feature'], feature_importance['importance'])
            axes[1,1].set_title('Feature Importance')
            axes[1,1].set_xlabel('Importance')
        else:
            axes[1,1].text(0.5, 0.5, 'Feature importance\nnot available for\nthis model type', 
                          ha='center', va='center', transform=axes[1,1].transAxes)
            axes[1,1].set_title('Feature Importance')
        
        # 6. Model performance by mood
        mood_accuracies = []
        for mood in self.mood_labels:
            mood_mask = (y_test == mood)
            if np.any(mood_mask):
                mood_accuracy = np.mean(y_pred[mood_mask] == mood)
                mood_accuracies.append(mood_accuracy)
            else:
                mood_accuracies.append(0)
        
        axes[1,2].bar(self.mood_labels, mood_accuracies, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        axes[1,2].set_title('Model Performance by Mood')
        axes[1,2].set_xlabel('Mood')
        axes[1,2].set_ylabel('Accuracy')
        axes[1,2].set_ylim(0, 1)
        
        plt.tight_layout()
        plt.savefig('milestone1_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()

    
    def predict_new_song(self, tempo, energy, valence, loudness, danceability=0.5, 
                        speechiness=0.1, acousticness=0.1, instrumentalness=0.1, liveness=0.1):
        """Predict mood for a new song"""
        if self.model is None:
            return "Model not trained yet!"
        
        # Create feature vector
        features = np.array([[tempo, energy, valence, loudness, danceability, 
                             speechiness, acousticness, instrumentalness, liveness]])
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Predict
        prediction = self.model.predict(features_scaled)[0]
        confidence = np.max(self.model.predict_proba(features_scaled))
        
        return prediction, confidence
    
    def save_model(self, filename='milestone1_model.pkl'):
        import joblib
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'mood_labels': self.mood_labels
        }, filename)
        print(f"Model saved as '{filename}'")
    
    def load_model(self, filename='milestone1_model.pkl'):
        """Load a trained model"""
        import joblib
        data = joblib.load(filename)
        self.model = data['model']
        self.scaler = data['scaler']
        self.mood_labels = data['mood_labels']
        print(f"Model loaded from '{filename}'")

def main():
    print("Song Mood Classification System")
    print("=" * 60)
    print("Using Dataset for Training and Evaluation")
    print("Goal: Basic end-to-end classifier working on labeled dataset")
    print()
    
    # Initialize classifier
    classifier = MoodClassifier()
    
    # Load dataset
    df = classifier.load_music_dataset()
    
    # Save dataset
    df.to_csv('music_dataset.csv', index=False)
    print("Dataset saved as 'music_dataset.csv'")
    
    # Train models
    results, X_test, y_test, y_pred = classifier.train_models(df)
    
    # Create visualizations
    classifier.create_visualizations(df, X_test, y_test, y_pred)
    
    # Save model
    classifier.save_model()
    
    # Demonstrate prediction
    print("\nTesting prediction on new song:")
    print("Example: Tempo=120, Energy=0.8, Valence=0.7, Loudness=-5")
    prediction, confidence = classifier.predict_new_song(120, 0.8, 0.7, -5)
    print(f"Predicted mood: {prediction} (confidence: {confidence:.3f})")

    return classifier, df

if __name__ == "__main__":
    classifier, dataset = main()
