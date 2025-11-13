"""
Compare Audio-based Predictions vs Lyrics-based Predictions
Simple comparison script for Milestone 2
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report

# Simple comparison function
def compare_predictions(df, audio_pred_col='audio_prediction', lyrics_pred_col='lyrics_prediction', 
                       true_label_col='mood'):
    """
    Compare audio predictions vs lyrics predictions.
    
    Args:
        df: DataFrame with predictions
        audio_pred_col: Column name with audio model predictions
        lyrics_pred_col: Column name with lyrics model predictions
        true_label_col: Column name with true labels (if available)
    
    Returns:
        Dictionary with comparison results
    """
    print("=" * 60)
    print("Comparing Audio vs Lyrics Predictions")
    print("=" * 60)
    print()
    
    # Filter out rows with missing predictions
    df_clean = df.dropna(subset=[audio_pred_col, lyrics_pred_col])
    
    if len(df_clean) == 0:
        print("ERROR: No rows with both audio and lyrics predictions found!")
        return None
    
    print(f"Comparing {len(df_clean)} songs with both predictions...")
    print()
    
    # Calculate agreement
    agreement = (df_clean[audio_pred_col] == df_clean[lyrics_pred_col]).sum()
    agreement_pct = (agreement / len(df_clean)) * 100
    
    print(f"Agreement: {agreement}/{len(df_clean)} ({agreement_pct:.1f}%)")
    print(f"Disagreement: {len(df_clean) - agreement}/{len(df_clean)} ({100 - agreement_pct:.1f}%)")
    print()
    
    # If true labels exist, calculate accuracy for each model
    if true_label_col in df_clean.columns:
        audio_accuracy = accuracy_score(df_clean[true_label_col], df_clean[audio_pred_col])
        lyrics_accuracy = accuracy_score(df_clean[true_label_col], df_clean[lyrics_pred_col])
        
        print("Accuracy (compared to true labels):")
        print(f"  Audio model:  {audio_accuracy:.3f} ({audio_accuracy*100:.1f}%)")
        print(f"  Lyrics model: {lyrics_accuracy:.3f} ({lyrics_accuracy*100:.1f}%)")
        print()
    
    # Agreement by mood
    print("Agreement by mood (audio vs lyrics):")
    moods = ['happy', 'chill', 'sad', 'hyped']
    for mood in moods:
        mood_df = df_clean[df_clean[audio_pred_col] == mood]
        if len(mood_df) > 0:
            mood_agreement = (mood_df[audio_pred_col] == mood_df[lyrics_pred_col]).sum()
            mood_agreement_pct = (mood_agreement / len(mood_df)) * 100
            print(f"  {mood:8s}: {mood_agreement}/{len(mood_df)} ({mood_agreement_pct:.1f}%)")
    print()
    
    # Find disagreement patterns
    disagreement_df = df_clean[df_clean[audio_pred_col] != df_clean[lyrics_pred_col]]
    if len(disagreement_df) > 0:
        print("Disagreement patterns (audio -> lyrics):")
        disagreement_patterns = disagreement_df.groupby([audio_pred_col, lyrics_pred_col]).size()
        for (audio, lyrics), count in disagreement_patterns.items():
            print(f"  {audio:8s} -> {lyrics:8s}: {count} songs")
        print()
    
    # Return results
    results = {
        'total_songs': len(df_clean),
        'agreement': agreement,
        'agreement_pct': agreement_pct,
        'disagreement': len(df_clean) - agreement,
        'disagreement_pct': 100 - agreement_pct,
    }
    
    if true_label_col in df_clean.columns:
        results['audio_accuracy'] = audio_accuracy
        results['lyrics_accuracy'] = lyrics_accuracy
    
    return results


def create_comparison_visualization(df, audio_pred_col='audio_prediction', 
                                   lyrics_pred_col='lyrics_prediction', 
                                   save_path='audio_lyrics_comparison.png'):
    """
    Create visualization showing where audio and lyrics predictions agree/disagree.
    
    Args:
        df: DataFrame with predictions
        audio_pred_col: Column name with audio predictions
        lyrics_pred_col: Column name with lyrics predictions
        save_path: Path to save the visualization
    """
    print(f"Creating visualization...")
    
    # Filter out rows with missing predictions
    df_clean = df.dropna(subset=[audio_pred_col, lyrics_pred_col])
    
    if len(df_clean) == 0:
        print("ERROR: No data to visualize!")
        return
    
    # Set up the plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle('Audio vs Lyrics Predictions Comparison', fontsize=16, fontweight='bold')
    
    moods = ['happy', 'chill', 'sad', 'hyped']
    
    # 1. Agreement vs Disagreement (pie chart)
    agreement = (df_clean[audio_pred_col] == df_clean[lyrics_pred_col]).sum()
    disagreement = len(df_clean) - agreement
    
    axes[0, 0].pie(
        [agreement, disagreement],
        labels=[f'Agree ({agreement})', f'Disagree ({disagreement})'],
        autopct='%1.1f%%',
        colors=['#4ECDC4', '#FF6B6B'],
        startangle=90
    )
    axes[0, 0].set_title('Agreement vs Disagreement')
    
    # 2. Confusion Matrix (Audio predictions vs Lyrics predictions)
    cm = confusion_matrix(df_clean[audio_pred_col], df_clean[lyrics_pred_col], labels=moods)
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=moods,
        yticklabels=moods,
        ax=axes[0, 1]
    )
    axes[0, 1].set_title('Confusion Matrix: Audio (rows) vs Lyrics (columns)')
    axes[0, 1].set_xlabel('Lyrics Prediction')
    axes[0, 1].set_ylabel('Audio Prediction')
    
    # 3. Distribution of predictions
    audio_counts = df_clean[audio_pred_col].value_counts().reindex(moods, fill_value=0)
    lyrics_counts = df_clean[lyrics_pred_col].value_counts().reindex(moods, fill_value=0)
    
    x = np.arange(len(moods))
    width = 0.35
    
    axes[1, 0].bar(x - width/2, audio_counts.values, width, label='Audio', color='#45B7D1')
    axes[1, 0].bar(x + width/2, lyrics_counts.values, width, label='Lyrics', color='#96CEB4')
    axes[1, 0].set_xlabel('Mood')
    axes[1, 0].set_ylabel('Number of Songs')
    axes[1, 0].set_title('Distribution of Predictions')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(moods)
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # 4. Agreement by mood
    agreement_by_mood = []
    for mood in moods:
        mood_df = df_clean[df_clean[audio_pred_col] == mood]
        if len(mood_df) > 0:
            mood_agreement = (mood_df[audio_pred_col] == mood_df[lyrics_pred_col]).sum()
            agreement_pct = (mood_agreement / len(mood_df)) * 100
            agreement_by_mood.append(agreement_pct)
        else:
            agreement_by_mood.append(0)
    
    axes[1, 1].bar(moods, agreement_by_mood, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    axes[1, 1].set_xlabel('Mood (Audio Prediction)')
    axes[1, 1].set_ylabel('Agreement %')
    axes[1, 1].set_title('Agreement Percentage by Mood')
    axes[1, 1].set_ylim(0, 100)
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, v in enumerate(agreement_by_mood):
        axes[1, 1].text(i, v + 2, f'{v:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved visualization to {save_path}")
    plt.show()


def main():
    """
    Example usage of the comparison script.
    """
    print("=" * 60)
    print("Audio vs Lyrics Predictions Comparison")
    print("=" * 60)
    print()
    
    # Example: Load dataset with predictions
    dataset_path = Path("data/processed/songs_with_predictions.csv")
    
    if not dataset_path.exists():
        print(f"Dataset not found at {dataset_path}")
        print("Please run the prediction scripts first to generate predictions.")
        print()
        print("Expected columns in dataset:")
        print("  - audio_prediction: Predictions from audio model")
        print("  - lyrics_prediction: Predictions from lyrics model")
        print("  - mood: True labels (optional)")
        return
    
    # Load dataset
    print(f"Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    
    # Check if required columns exist
    if 'audio_prediction' not in df.columns or 'lyrics_prediction' not in df.columns:
        print("ERROR: Required columns not found in dataset!")
        print("Expected columns: audio_prediction, lyrics_prediction")
        print(f"Found columns: {list(df.columns)}")
        return
    
    # Compare predictions
    results = compare_predictions(
        df,
        audio_pred_col='audio_prediction',
        lyrics_pred_col='lyrics_prediction',
        true_label_col='mood' if 'mood' in df.columns else None
    )
    
    # Create visualization
    create_comparison_visualization(
        df,
        audio_pred_col='audio_prediction',
        lyrics_pred_col='lyrics_prediction',
        save_path='audio_lyrics_comparison.png'
    )
    
    print("\nComparison complete!")


if __name__ == "__main__":
    main()

