"""
Enhanced Visualizations for Milestone 2
Includes:
- 3a. Confidence bar chart (probability distribution)
- 3b. Mood map (2D feature space visualization)
- 3d. Enhanced audio vs lyrics comparison (side-by-side)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import joblib
import sys
import warnings
warnings.filterwarnings("ignore")

# For mood map
try:
    from sklearn.manifold import TSNE
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    TSNE_AVAILABLE = True
except ImportError:
    TSNE_AVAILABLE = False

# Import audio data utilities
sys.path.append(str(Path(__file__).parent))
from audio_data import load_audio_data, TARGETS, FEATURE_WISHLIST

# Resolve paths relative to project root (parent of src directory)
BASE = Path(__file__).resolve().parents[1]
FIG_DIR = BASE / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = BASE / "models" / "new_song_mood_model.joblib"


# 3a. Confidence distributions - separate files

def plot_audio_confidence_distribution(save_path=None):
    """Audio model confidence distribution histogram"""
    if save_path is None:
        save_path = FIG_DIR / "audio_confidence_distribution.png"
    
    try:
        if not MODEL_PATH.exists():
            print(f"WARNING: Audio model not found at {MODEL_PATH}")
            return
        
        bundle = joblib.load(MODEL_PATH)
        model = bundle['pipeline']
        X_train, X_test, y_train, y_test, feature_names = load_audio_data()
        
        proba_audio = model.predict_proba(X_test)
        max_conf_audio = proba_audio.max(axis=1)
        
        plt.figure(figsize=(10, 6))
        plt.hist(max_conf_audio, bins=30, alpha=0.7, color='#45B7D1', edgecolor='black')
        plt.axvline(max_conf_audio.mean(), color='red', linestyle='--', 
                   label=f'Mean: {max_conf_audio.mean():.3f}')
        plt.xlabel('Maximum Prediction Confidence')
        plt.ylabel('Number of Songs')
        plt.title('Audio Model: Confidence Distribution')
        plt.grid(True, alpha=0.3, axis='y')
        plt.legend()
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved: {save_path}")
    except Exception as e:
        print(f"ERROR creating audio confidence distribution: {e}")


def plot_lyrics_confidence_distribution(df, lyrics_conf_col='lyrics_confidence', save_path=None):
    """Lyrics model confidence distribution histogram"""
    if save_path is None:
        save_path = FIG_DIR / "lyrics_confidence_distribution.png"
    
    if lyrics_conf_col not in df.columns:
        print(f"WARNING: Column '{lyrics_conf_col}' not found")
        return
    
    conf_lyrics = df[lyrics_conf_col].dropna()
    if len(conf_lyrics) == 0:
        print("WARNING: No confidence data available")
        return
    
    plt.figure(figsize=(10, 6))
    plt.hist(conf_lyrics, bins=30, alpha=0.7, color='#96CEB4', edgecolor='black')
    plt.axvline(conf_lyrics.mean(), color='red', linestyle='--', 
               label=f'Mean: {conf_lyrics.mean():.3f}')
    plt.xlabel('Prediction Confidence')
    plt.ylabel('Number of Songs')
    plt.title('Lyrics Model: Confidence Distribution')
    plt.grid(True, alpha=0.3, axis='y')
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_audio_confidence_by_mood(save_path=None):
    """Audio model mean confidence by predicted mood"""
    if save_path is None:
        save_path = FIG_DIR / "audio_confidence_by_mood.png"
    
    moods = ['happy', 'chill', 'sad', 'hyped']
    
    try:
        if not MODEL_PATH.exists():
            print(f"WARNING: Audio model not found at {MODEL_PATH}")
            return
        
        bundle = joblib.load(MODEL_PATH)
        model = bundle['pipeline']
        X_train, X_test, y_train, y_test, feature_names = load_audio_data()
        
        y_pred_audio = model.predict(X_test)
        proba_audio = model.predict_proba(X_test)
        max_conf_audio = proba_audio.max(axis=1)
        
        conf_by_mood = []
        mood_labels = []
        for mood in moods:
            mask = y_pred_audio == mood
            if mask.sum() > 0:
                conf_by_mood.append(max_conf_audio[mask].mean())
                mood_labels.append(mood)
        
        plt.figure(figsize=(10, 6))
        plt.bar(mood_labels, conf_by_mood, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        plt.xlabel('Predicted Mood')
        plt.ylabel('Mean Confidence')
        plt.title('Audio Model: Mean Confidence by Predicted Mood')
        plt.ylim(0, 1)
        plt.grid(True, alpha=0.3, axis='y')
        for i, v in enumerate(conf_by_mood):
            plt.text(i, v + 0.02, f'{v:.3f}', ha='center', va='bottom')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved: {save_path}")
    except Exception as e:
        print(f"ERROR creating audio confidence by mood: {e}")


def plot_lyrics_confidence_by_mood(df, lyrics_pred_col='lyrics_prediction',
                                   lyrics_conf_col='lyrics_confidence', save_path=None):
    """Lyrics model mean confidence by predicted mood"""
    if save_path is None:
        save_path = FIG_DIR / "lyrics_confidence_by_mood.png"
    
    moods = ['happy', 'chill', 'sad', 'hyped']
    df_clean = df.dropna(subset=[lyrics_pred_col, lyrics_conf_col])
    
    if len(df_clean) == 0:
        print("WARNING: No data available")
        return
    
    conf_by_mood = []
    mood_labels = []
    for mood in moods:
        mood_df = df_clean[df_clean[lyrics_pred_col] == mood]
        if len(mood_df) > 0:
            conf_by_mood.append(mood_df[lyrics_conf_col].mean())
            mood_labels.append(mood)
    
    if len(conf_by_mood) == 0:
        print("WARNING: No confidence data by mood")
        return
    
    plt.figure(figsize=(10, 6))
    plt.bar(mood_labels, conf_by_mood, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    plt.xlabel('Predicted Mood')
    plt.ylabel('Mean Confidence')
    plt.title('Lyrics Model: Mean Confidence by Predicted Mood')
    plt.ylim(0, 1)
    plt.grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(conf_by_mood):
        plt.text(i, v + 0.02, f'{v:.3f}', ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_mood_map(df=None, method='tsne', n_samples=5000, save_path=None):
    """
    3b. Mood map - 2D visualization of songs in feature space
    
    Args:
        df: Optional DataFrame with features (if None, loads from audio_data)
        method: 'tsne' or 'pca' for dimensionality reduction
        n_samples: Number of samples to plot (for performance)
        save_path: Path to save figure
    """
    if save_path is None:
        save_path = FIG_DIR / f"mood_map_{method}.png"
    
    if not TSNE_AVAILABLE:
        print("ERROR: sklearn not available. Cannot create mood map.")
        return
    
    print(f"Creating {method.upper()} mood map (sampling {n_samples} songs)...")
    
    try:
        # Load audio data
        if df is None:
            X_train, X_test, y_train, y_test, feature_names = load_audio_data()
            X_all = pd.concat([X_train, X_test])
            y_all = pd.concat([y_train, y_test])
        else:
            # Use provided dataframe
            feature_names = [f for f in FEATURE_WISHLIST if f in df.columns]
            if len(feature_names) == 0:
                print("ERROR: No audio features found in dataframe")
                return
            
            X_all = df[feature_names].copy()
            if 'mood' in df.columns:
                y_all = df['mood']
            else:
                print("WARNING: No 'mood' column found. Using predictions if available.")
                y_all = None
        
        # Sample if too many points
        if len(X_all) > n_samples:
            sample_idx = np.random.choice(len(X_all), n_samples, replace=False)
            X_sample = X_all.iloc[sample_idx].copy()
            y_sample = y_all.iloc[sample_idx] if y_all is not None else None
        else:
            X_sample = X_all.copy()
            y_sample = y_all.copy() if y_all is not None else None
        
        # Handle missing values
        X_sample = X_sample.fillna(X_sample.median())
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_sample)
        
        # Apply dimensionality reduction
        if method.lower() == 'tsne':
            # Optimize t-SNE: reduce perplexity and iterations for speed
            # Perplexity should be < n_samples, so adjust based on sample size
            perplexity = min(30, max(5, n_samples // 100))
            n_iter = 500  # Reduced from 1000 for speed
            reducer = TSNE(n_components=2, random_state=42, perplexity=perplexity, n_iter=n_iter)
            print(f"Computing t-SNE embedding (perplexity={perplexity}, iterations={n_iter})...")
            print("(This may take 1-3 minutes for 5000 samples...)")
        elif method.lower() == 'pca':
            reducer = PCA(n_components=2, random_state=42)
            print("Computing PCA embedding (fast)...")
        else:
            print(f"ERROR: Unknown method '{method}'. Use 'tsne' or 'pca'.")
            return
        
        X_2d = reducer.fit_transform(X_scaled)
        print(f"✓ {method.upper()} embedding complete!")
        
        # Create plot
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Color map for moods
        mood_colors = {
            'happy': '#FF6B6B',
            'chill': '#4ECDC4',
            'sad': '#45B7D1',
            'hyped': '#96CEB4'
        }
        
        if y_sample is not None:
            # Plot by true mood
            for mood in TARGETS:
                mask = y_sample == mood
                if mask.sum() > 0:
                    ax.scatter(X_2d[mask, 0], X_2d[mask, 1], 
                             c=mood_colors.get(mood, 'gray'), 
                             label=mood, alpha=0.6, s=20)
            
            ax.legend(title='Mood', loc='best')
            title_suffix = '(True Labels)'
        else:
            # No labels, just plot all points
            ax.scatter(X_2d[:, 0], X_2d[:, 1], alpha=0.6, s=20, c='blue')
            title_suffix = '(No Labels)'
        
        method_name = 't-SNE' if method.lower() == 'tsne' else 'PCA'
        ax.set_title(f'{method_name} Mood Map: 2D Feature Space Visualization {title_suffix}', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel(f'{method_name} Component 1')
        ax.set_ylabel(f'{method_name} Component 2')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved mood map to {save_path}")
        plt.close()
        
    except Exception as e:
        print(f"ERROR creating mood map: {e}")
        import traceback
        traceback.print_exc()


# 3d. Audio vs Lyrics comparison - separate files

def plot_audio_prediction_distribution(df, audio_pred_col='audio_prediction', save_path=None):
    """Audio model prediction distribution"""
    if save_path is None:
        save_path = FIG_DIR / "audio_prediction_distribution.png"
    
    moods = ['happy', 'chill', 'sad', 'hyped']
    df_clean = df.dropna(subset=[audio_pred_col])
    audio_counts = df_clean[audio_pred_col].value_counts().reindex(moods, fill_value=0)
    
    plt.figure(figsize=(10, 6))
    plt.bar(audio_counts.index, audio_counts.values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    plt.xlabel('Mood')
    plt.ylabel('Number of Songs')
    plt.title('Audio Model: Prediction Distribution')
    plt.grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(audio_counts.values):
        plt.text(i, v + max(audio_counts.values)*0.01, f'{v:,}', ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_lyrics_prediction_distribution(df, lyrics_pred_col='lyrics_prediction', save_path=None):
    """Lyrics model prediction distribution"""
    if save_path is None:
        save_path = FIG_DIR / "lyrics_prediction_distribution.png"
    
    moods = ['happy', 'chill', 'sad', 'hyped']
    df_clean = df.dropna(subset=[lyrics_pred_col])
    lyrics_counts = df_clean[lyrics_pred_col].value_counts().reindex(moods, fill_value=0)
    
    plt.figure(figsize=(10, 6))
    plt.bar(lyrics_counts.index, lyrics_counts.values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    plt.xlabel('Mood')
    plt.ylabel('Number of Songs')
    plt.title('Lyrics Model: Prediction Distribution')
    plt.grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(lyrics_counts.values):
        plt.text(i, v + max(lyrics_counts.values)*0.01, f'{v:,}', ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_audio_lyrics_agreement_pie(df, audio_pred_col='audio_prediction',
                                    lyrics_pred_col='lyrics_prediction', save_path=None):
    """Overall agreement pie chart"""
    if save_path is None:
        save_path = FIG_DIR / "audio_lyrics_agreement_pie.png"
    
    df_clean = df.dropna(subset=[audio_pred_col, lyrics_pred_col])
    agreement = (df_clean[audio_pred_col] == df_clean[lyrics_pred_col]).sum()
    disagreement = len(df_clean) - agreement
    
    plt.figure(figsize=(10, 8))
    plt.pie([agreement, disagreement],
           labels=[f'Agree\n{agreement:,} songs\n({agreement/len(df_clean)*100:.1f}%)',
                  f'Disagree\n{disagreement:,} songs\n({disagreement/len(df_clean)*100:.1f}%)'],
           autopct='', colors=['#4ECDC4', '#FF6B6B'], startangle=90,
           textprops={'fontsize': 12, 'fontweight': 'bold'})
    plt.title('Overall Agreement: Audio vs Lyrics', fontweight='bold', fontsize=14)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_audio_lyrics_distribution_comparison(df, audio_pred_col='audio_prediction',
                                             lyrics_pred_col='lyrics_prediction', save_path=None):
    """Side-by-side distribution comparison"""
    if save_path is None:
        save_path = FIG_DIR / "audio_lyrics_distribution_comparison.png"
    
    moods = ['happy', 'chill', 'sad', 'hyped']
    df_clean = df.dropna(subset=[audio_pred_col, lyrics_pred_col])
    audio_counts = df_clean[audio_pred_col].value_counts().reindex(moods, fill_value=0)
    lyrics_counts = df_clean[lyrics_pred_col].value_counts().reindex(moods, fill_value=0)
    
    x = np.arange(len(moods))
    width = 0.35
    
    plt.figure(figsize=(12, 7))
    plt.bar(x - width/2, audio_counts.values, width, label='Audio', color='#45B7D1', alpha=0.8)
    plt.bar(x + width/2, lyrics_counts.values, width, label='Lyrics', color='#96CEB4', alpha=0.8)
    plt.xlabel('Mood')
    plt.ylabel('Number of Songs')
    plt.title('Prediction Distribution: Audio vs Lyrics')
    plt.xticks(x, moods)
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_audio_lyrics_confusion_matrix(df, audio_pred_col='audio_prediction',
                                      lyrics_pred_col='lyrics_prediction', save_path=None):
    """Audio vs Lyrics predictions confusion matrix"""
    if save_path is None:
        save_path = FIG_DIR / "audio_lyrics_confusion_matrix.png"
    
    moods = ['happy', 'chill', 'sad', 'hyped']
    df_clean = df.dropna(subset=[audio_pred_col, lyrics_pred_col])
    from sklearn.metrics import confusion_matrix
    
    cm_comparison = confusion_matrix(df_clean[audio_pred_col], df_clean[lyrics_pred_col], labels=moods)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm_comparison, annot=True, fmt='d', cmap='Oranges',
               xticklabels=moods, yticklabels=moods)
    plt.title('Audio (rows) vs Lyrics (columns) Predictions', fontweight='bold')
    plt.xlabel('Lyrics Prediction')
    plt.ylabel('Audio Prediction')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_audio_agreement_by_mood(df, audio_pred_col='audio_prediction',
                                 lyrics_pred_col='lyrics_prediction', save_path=None):
    """Audio model agreement % by mood"""
    if save_path is None:
        save_path = FIG_DIR / "audio_agreement_by_mood.png"
    
    moods = ['happy', 'chill', 'sad', 'hyped']
    df_clean = df.dropna(subset=[audio_pred_col, lyrics_pred_col])
    
    agreement_by_mood = []
    for mood in moods:
        mood_df = df_clean[df_clean[audio_pred_col] == mood]
        if len(mood_df) > 0:
            agreement = (mood_df[audio_pred_col] == mood_df[lyrics_pred_col]).sum()
            agreement_pct = (agreement / len(mood_df)) * 100
            agreement_by_mood.append(agreement_pct)
        else:
            agreement_by_mood.append(0)
    
    plt.figure(figsize=(10, 6))
    plt.bar(moods, agreement_by_mood, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    plt.xlabel('Audio Prediction')
    plt.ylabel('Agreement %')
    plt.title('Audio Model: Agreement % by Mood')
    plt.ylim(0, 100)
    plt.grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(agreement_by_mood):
        plt.text(i, v + 2, f'{v:.1f}%', ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_lyrics_agreement_by_mood(df, audio_pred_col='audio_prediction',
                                  lyrics_pred_col='lyrics_prediction', save_path=None):
    """Lyrics model agreement % by mood"""
    if save_path is None:
        save_path = FIG_DIR / "lyrics_agreement_by_mood.png"
    
    moods = ['happy', 'chill', 'sad', 'hyped']
    df_clean = df.dropna(subset=[audio_pred_col, lyrics_pred_col])
    
    agreement_by_mood = []
    for mood in moods:
        mood_df = df_clean[df_clean[lyrics_pred_col] == mood]
        if len(mood_df) > 0:
            agreement = (mood_df[audio_pred_col] == mood_df[lyrics_pred_col]).sum()
            agreement_pct = (agreement / len(mood_df)) * 100
            agreement_by_mood.append(agreement_pct)
        else:
            agreement_by_mood.append(0)
    
    plt.figure(figsize=(10, 6))
    plt.bar(moods, agreement_by_mood, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    plt.xlabel('Lyrics Prediction')
    plt.ylabel('Agreement %')
    plt.title('Lyrics Model: Agreement % by Mood')
    plt.ylim(0, 100)
    plt.grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(agreement_by_mood):
        plt.text(i, v + 2, f'{v:.1f}%', ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_audio_confusion_matrix_vs_true(df, audio_pred_col='audio_prediction',
                                       true_label_col='mood', save_path=None):
    """Audio model confusion matrix vs true labels"""
    if save_path is None:
        save_path = FIG_DIR / "audio_confusion_matrix_vs_true.png"
    
    moods = ['happy', 'chill', 'sad', 'hyped']
    df_clean = df.dropna(subset=[audio_pred_col, true_label_col])
    
    from sklearn.metrics import confusion_matrix
    cm_audio = confusion_matrix(df_clean[true_label_col], df_clean[audio_pred_col], labels=moods)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm_audio, annot=True, fmt='d', cmap='Blues',
               xticklabels=moods, yticklabels=moods)
    plt.title('Audio Model: Confusion Matrix vs True Labels', fontweight='bold')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_low_confidence_by_mood(df,
                                audio_low_col='audio_low_confidence',
                                lyrics_low_col='lyrics_low_confidence',
                                audio_pred_col='audio_prediction',
                                lyrics_pred_col='lyrics_prediction',
                                save_path=None):
    """
    Uncertainty plot: percentage of low-confidence predictions by mood
    for both audio and lyrics models.
    """
    if save_path is None:
        save_path = FIG_DIR / "uncertainty_by_mood.png"

    moods = ['happy', 'chill', 'sad', 'hyped']
    df_clean = df.copy()

    if audio_low_col not in df_clean.columns or lyrics_low_col not in df_clean.columns:
        print("WARNING: low-confidence columns not found; skipping uncertainty_by_mood plot.")
        return

    audio_rates = []
    lyrics_rates = []

    for mood in moods:
        # Audio: group by audio prediction
        mood_df_audio = df_clean[df_clean[audio_pred_col] == mood]
        if len(mood_df_audio) > 0:
            audio_rates.append(100.0 * mood_df_audio[audio_low_col].mean())
        else:
            audio_rates.append(0.0)

        # Lyrics: group by lyrics prediction
        mood_df_lyrics = df_clean[df_clean[lyrics_pred_col] == mood]
        if len(mood_df_lyrics) > 0:
            lyrics_rates.append(100.0 * mood_df_lyrics[lyrics_low_col].mean())
        else:
            lyrics_rates.append(0.0)

    x = np.arange(len(moods))
    width = 0.35

    plt.figure(figsize=(10, 6))
    plt.bar(x - width/2, audio_rates, width, label='Audio', color='#45B7D1')
    plt.bar(x + width/2, lyrics_rates, width, label='Lyrics', color='#96CEB4')
    plt.xlabel('Predicted Mood')
    plt.ylabel('Low-confidence %')
    plt.title('Low-confidence Predictions by Mood (Audio vs Lyrics)')
    plt.xticks(x, moods)
    plt.ylim(0, 100)
    plt.grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(audio_rates):
        plt.text(i - width/2, v + 1, f'{v:.1f}%', ha='center', va='bottom', fontsize=8)
    for i, v in enumerate(lyrics_rates):
        plt.text(i + width/2, v + 1, f'{v:.1f}%', ha='center', va='bottom', fontsize=8)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_low_confidence_hist(df,
                             model='audio',
                             conf_col_audio='audio_confidence',
                             conf_col_lyrics='lyrics_confidence',
                             low_flag_audio='audio_low_confidence',
                             low_flag_lyrics='lyrics_low_confidence',
                             save_path=None):
    """
    Histogram of low-confidence predictions only, for audio or lyrics model.
    """
    if model == 'audio':
        conf_col = conf_col_audio
        flag_col = low_flag_audio
        default_name = "audio_low_conf_hist.png"
        color = '#45B7D1'
        title = 'Audio Model: Low-confidence Predictions'
    else:
        conf_col = conf_col_lyrics
        flag_col = low_flag_lyrics
        default_name = "lyrics_low_conf_hist.png"
        color = '#96CEB4'
        title = 'Lyrics Model: Low-confidence Predictions'

    if save_path is None:
        save_path = FIG_DIR / default_name

    if conf_col not in df.columns or flag_col not in df.columns:
        print(f"WARNING: columns '{conf_col}' or '{flag_col}' not found; skipping low-confidence histogram for {model}.")
        return

    df_low = df[df[flag_col]].copy()
    if df_low.empty:
        print(f"WARNING: no low-confidence samples for {model}; skipping histogram.")
        return

    vals = df_low[conf_col].dropna()
    if vals.empty:
        print(f"WARNING: no confidence values for low-confidence {model} samples; skipping histogram.")
        return

    plt.figure(figsize=(8, 5))
    plt.hist(vals, bins=20, color=color, edgecolor='black', alpha=0.8)
    plt.xlabel('Prediction confidence')
    plt.ylabel('Number of songs')
    plt.title(title)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")

def plot_lyrics_confusion_matrix_vs_true(df, lyrics_pred_col='lyrics_prediction',
                                        true_label_col='mood', save_path=None):
    """Lyrics model confusion matrix vs true labels"""
    if save_path is None:
        save_path = FIG_DIR / "lyrics_confusion_matrix_vs_true.png"
    
    moods = ['happy', 'chill', 'sad', 'hyped']
    df_clean = df.dropna(subset=[lyrics_pred_col, true_label_col])
    
    from sklearn.metrics import confusion_matrix
    cm_lyrics = confusion_matrix(df_clean[true_label_col], df_clean[lyrics_pred_col], labels=moods)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm_lyrics, annot=True, fmt='d', cmap='Greens',
               xticklabels=moods, yticklabels=moods)
    plt.title('Lyrics Model: Confusion Matrix vs True Labels', fontweight='bold')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def main():
    """Main function to create all enhanced visualizations - one PNG per chart"""
    print("=" * 60)
    print("Enhanced Visualizations for Milestone 2")
    print("Creating one PNG file per visualization")
    print("=" * 60)
    print()
    
    # Check if predictions file exists
    predictions_path = Path("data/processed/songs_with_predictions.csv")
    
    if not predictions_path.exists():
        print(f"ERROR: Predictions file not found at {predictions_path}")
        print("Please run run_lyrics_comparison.py first to generate predictions.")
        return
    
    # Load predictions
    print(f"Loading predictions from {predictions_path}...")
    df = pd.read_csv(predictions_path)
    print(f"Loaded {len(df)} songs")
    print()
    
    # 3a. Confidence distributions (4 separate files)
    print("3a. Creating confidence distribution charts...")
    plot_audio_confidence_distribution()
    plot_lyrics_confidence_distribution(df)
    plot_audio_confidence_by_mood()
    plot_lyrics_confidence_by_mood(df)
    print()
    
    # 3b. Mood maps (2 separate files)
    print("3b. Creating mood maps...")
    print("  - PCA (fast)...")
    plot_mood_map(df=None, method='pca', n_samples=10000)
    print("  - t-SNE (this may take 2-3 minutes)...")
    plot_mood_map(df=None, method='tsne', n_samples=3000)
    print()
    
    # 3d. Audio vs Lyrics comparisons (9 separate files)
    print("3d. Creating audio vs lyrics comparisons...")
    plot_audio_prediction_distribution(df)
    plot_lyrics_prediction_distribution(df)
    plot_audio_lyrics_agreement_pie(df)
    plot_audio_lyrics_distribution_comparison(df)
    plot_audio_lyrics_confusion_matrix(df)
    plot_audio_agreement_by_mood(df)
    plot_lyrics_agreement_by_mood(df)
    if 'mood' in df.columns:
        plot_audio_confusion_matrix_vs_true(df)
        plot_lyrics_confusion_matrix_vs_true(df)
    print()
    
    print("=" * 60)
    print("All enhanced visualizations created!")
    print(f"Figures saved in: {FIG_DIR}")
    print("Each visualization saved as a separate PNG file")
    print("=" * 60)


if __name__ == "__main__":
    main()

