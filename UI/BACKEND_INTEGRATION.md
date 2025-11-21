# Backend Integration Guide

## ✅ What's Been Done

### 1. Backend API Server (`src/api_server.py`)
- ✅ Flask API server running on port 8000
- ✅ Endpoint: `POST /api/predict`
- ✅ Automatically searches dataset for songs and lyrics
- ✅ Returns predictions in correct format

### 2. Frontend Component Updated (`UI/components/prediction-interface.tsx`)
- ✅ Connected to backend API
- ✅ Replaced mock data with real API calls
- ✅ Added error handling
- ✅ Supports parsing "Song Name by Artist" format

---

## 📋 API Interface

### Request Format:
```typescript
POST /api/predict
Content-Type: application/json

{
  "song": "Happy",              // Required
  "artist": "Pharrell Williams" // Optional (defaults to "Unknown Artist")
}
```

### Response Format:
```typescript
{
  "song": string,
  "artist": string,
  "audio": {
    "mood": "happy" | "chill" | "sad" | "hyped",
    "confidence": number,
    "lowConfidence": boolean
  },
  "lyrics": {
    "mood": "happy" | "chill" | "sad" | "hyped",
    "confidence": number,
    "lowConfidence": boolean
  } | null,
  "agree": boolean | null
}
```

---

## 🚀 How to Run

### 1. Start Backend:
```bash
cd src
python api_server.py
```

Server will start at: `http://localhost:8000`

### 2. Start Frontend:
```bash
cd UI
npm run dev
# or
pnpm dev
```

Frontend will start at: `http://localhost:3000`

### 3. Test the Integration:
1. Open `http://localhost:3000` in browser
2. Go to "Try the Classifier" section
3. Enter a song name (e.g., "Happy" or "Happy by Pharrell Williams")
4. Click "Predict"
5. Should see real predictions from your models!

---

## 🔧 Configuration

### Environment Variables (Optional):

Create `UI/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

If not set, defaults to `http://localhost:8000`

---

## 🐛 Troubleshooting

### Error: "Song not found in dataset"
- **Cause**: Song doesn't exist in your dataset files
- **Solution**: 
  - Enter a song that exists in your CSV files
  - Or provide `audio_features` in the request body (future enhancement)

### Error: "Audio model not loaded"
- **Cause**: Model file missing
- **Solution**: Make sure `models/new_song_mood_model.joblib` exists
  - Run `python src/train_from_mapped.py` first

### Error: CORS errors
- **Cause**: Backend not allowing frontend origin
- **Solution**: Already fixed with `CORS(app)` in `api_server.py`

### Error: Connection refused
- **Cause**: Backend not running
- **Solution**: Start the backend server first (`python src/api_server.py`)

---

## 📝 How It Works

1. **User enters song name** in frontend
2. **Frontend sends POST request** to `/api/predict` with song name
3. **Backend searches dataset** for the song:
   - Looks in `songs_balanced_sample.csv` first
   - Then `songs_mapped.csv`
   - Then `songs_with_predictions.csv`
4. **Backend extracts features**:
   - Audio features (tempo, energy, valence, etc.)
   - Lyrics text (if available)
5. **Backend runs predictions**:
   - Audio model (Random Forest) → mood prediction + confidence
   - Lyrics classifier (VADER) → mood prediction + confidence
6. **Backend returns formatted response**
7. **Frontend displays predictions** with confidence scores

---

## ✅ Verification Checklist

- [ ] Backend server runs without errors
- [ ] Frontend can connect to backend (no CORS errors)
- [ ] Predictions display correctly
- [ ] Confidence scores show properly
- [ ] Low-confidence warnings appear when appropriate
- [ ] Error messages display when song not found
- [ ] Agreement/disagreement badge works

---

## 🎯 Next Steps (Optional)

### Future Enhancements:
1. Add more API endpoints for other components (model-comparison, uncertainty-analysis)
2. Support manual feature input if song not in dataset
3. Add Spotify API integration for real-time song lookup
4. Add caching for frequently searched songs
5. Add batch prediction endpoint

---

## 📚 Code Locations

- **Backend API**: `src/api_server.py`
- **Frontend Component**: `UI/components/prediction-interface.tsx`
- **Model Files**: `models/new_song_mood_model.joblib`
- **Dataset Files**: `data/processed/songs_*.csv`

