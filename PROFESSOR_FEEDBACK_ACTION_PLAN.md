# Professor Feedback - Action Plan

## 🔴 CRITICAL CHANGES

### 1. **Clarify Methodology: Main Method vs Baseline**

**Current Issue:** Report doesn't clearly distinguish main method from baseline

**What to Change:**
- ✅ **Main Method:** Audio classifier (Random Forest with 9 audio features) - THIS IS YOUR CONTRIBUTION
- ✅ **Baseline/Comparison:** Lyrics classifier (VADER, NOT trained) - THIS IS FOR COMPARISON ONLY

**Text to Update:**
- Change: "Implemented Audio and Lyrics Classifiers"
- To: "Implemented Audio Classifier (Main Method) and Lyrics Baseline (Comparison)"

**Why:** The lyrics classifier is a baseline for comparison, NOT a trained model. It's VADER sentiment analysis, not machine learning.

---

### 2. **Create Balanced Dataset**

**Current Issue:** Dataset too large, class imbalance not addressed

**Action Required:**
- ✅ Created `src/create_balanced_sample.py` script
- Run it to create balanced sample (equal samples from each mood)
- Update `run_lyrics_comparison.py` to use balanced sample instead of full dataset

**Steps:**
1. Run: `python src/create_balanced_sample.py`
2. This creates `data/processed/songs_balanced_sample.csv`
3. Update scripts to use balanced sample instead of full dataset

---

### 3. **Add Feature Engineering Section**

**Current Issue:** Missing justification for which features to include

**What to Add:**

**Section: Feature Engineering**

We selected 9 audio features for mood classification:
- **Tempo (BPM)**: Captures song speed/energy level
- **Energy**: Measures intensity and power of the song
- **Valence**: Represents musical positiveness (happiness/sadness)
- **Loudness (dB)**: Overall volume of the track
- **Danceability**: How suitable a track is for dancing
- **Speechiness**: Presence of spoken words in a track
- **Acousticness**: Confidence measure of whether track is acoustic
- **Instrumentalness**: Predicts whether track contains vocals
- **Liveness**: Detects presence of audience in recording

**Selection Rationale:**
These features were chosen because they directly capture musical characteristics that correlate with emotional content. For example, tempo and energy distinguish "hyped" from "chill" moods, while valence separates "happy" from "sad" moods.

*For detailed feature descriptions and distributions, see Appendix A.*

---

### 4. **Fix Figure Issues**

**Current Issues:**
- Text too small in figures
- Missing figure captions
- Not eye-catching

**Action Required:**

**A. Increase Font Sizes:**
- Titles: fontsize=16 (currently ~14)
- Labels: fontsize=12 (currently ~10)
- Legends: fontsize=11 (currently ~10)
- Annotations: fontsize=10 (currently 8)

**B. Add Figure Captions:**
- Every figure needs a descriptive caption below it
- Format: "Figure X: [Description of what is shown]"

**C. Make More Eye-Catching:**
- Increase figure size (figsize=(12, 8) instead of (10, 6))
- Better color schemes (more vibrant)
- Clearer legends and labels

**Example Fix:**
```python
# OLD:
plt.figure(figsize=(10, 6))
plt.title('Low-confidence Predictions by Mood', fontsize=12)
plt.text(i, v + 1, f'{v:.1f}%', fontsize=8)

# NEW:
plt.figure(figsize=(12, 8))
plt.title('Low-confidence Predictions by Mood', fontsize=16, fontweight='bold')
plt.text(i, v + 1, f'{v:.1f}%', fontsize=12, fontweight='bold')
```

---

### 5. **Clarify OpenAI Cost**

**Current Issue:** May have overstated cost

**What to Say:**
- "OpenAI API was initially considered for lyrics classification, but proved expensive for large-scale processing (500k+ songs). We switched to VADER (free, local) for scalability."

**Why:** This is accurate - OpenAI is cheap per call, but expensive for large datasets.

---

### 6. **Report Structure Updates**

**Add/Update Sections:**

**A. Methodology Section:**
```
3. Methodology

3.1 Main Method: Audio-Based Mood Classification
   - Random Forest classifier
   - 9 audio features
   - Feature engineering (see Section 3.1.1)
   - Training details

3.2 Baseline Comparison: Lyrics-Based Classification
   - VADER sentiment analysis (NOT trained)
   - Used for comparison only
   - Simple rule-based mapping
```

**B. Feature Engineering Section:**
- Add Section 3.1.1 on feature selection
- Justify each feature
- Reference appendix for details

**C. Figure Captions:**
- Add caption below every figure
- Format: "Figure X: [Description]"

**D. Appendix:**
- Feature descriptions
- Detailed distributions
- Additional visualizations

---

## 🟡 MODERATE PRIORITY

### 7. **LLM Optimization Note**

**What to Add:**
- If mentioning LLMs, note that VADER is optimized for sentiment analysis
- Or mention that future work could use optimized LLMs (if relevant)

---

### 8. **Mention Audio Features in Report**

**Current Issue:** May not emphasize audio features enough

**What to Add:**
- Explicitly mention all 9 audio features used
- Explain why audio features are the main method
- "See Appendix for detailed feature analysis"

---

## ✅ COMPLETED ACTIONS

1. ✅ Created balanced sampling script (`create_balanced_sample.py`)
2. ✅ Identified all required changes
3. ✅ Documented action plan

---

## 📋 CHECKLIST

- [ ] Run balanced sampling script
- [ ] Update report to clarify main method vs baseline
- [ ] Add feature engineering section with justification
- [ ] Fix all figure font sizes (increase by 2-4 points)
- [ ] Add captions to all figures
- [ ] Update methodology section structure
- [ ] Add appendix section reference
- [ ] Clarify OpenAI cost statement
- [ ] Emphasize audio features throughout report
- [ ] Review all figures for readability

---

## 🎯 PRIORITY ORDER

1. **Run balanced sampling** (affects all results)
2. **Fix figure readability** (font sizes, captions)
3. **Clarify methodology** (main method vs baseline)
4. **Add feature engineering section**
5. **Update report structure**

---

## 📝 EXAMPLE TEXT CHANGES

### Methodology Section Update:
```
We implemented two mood classification approaches:

**Main Method: Audio-Based Classification**
We trained a Random Forest classifier using 9 audio features (tempo, energy, 
valence, loudness, danceability, speechiness, acousticness, instrumentalness, 
liveness). Feature selection and engineering details are provided in Section 3.1.1.

**Baseline Comparison: Lyrics-Based Classification**
For comparison, we used VADER sentiment analysis (not trained) to classify 
songs based on lyrics. This serves as a baseline to highlight differences 
between audio and lyrics signals, not as a trained model.
```

---

## 🔧 TECHNICAL FIXES NEEDED

### Update `run_lyrics_comparison.py`:
- Change to use balanced sample instead of full dataset
- Update path to `songs_balanced_sample.csv`

### Update visualization functions:
- Increase all font sizes
- Add caption parameter to all plot functions
- Save captions with figures or document separately

---

Let me know which items you'd like help implementing first!

