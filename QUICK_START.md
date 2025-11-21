# Quick Start Guide - Backend & Frontend Integration

## ✅ What's Complete

1. **Backend API** (`src/api_server.py`) - Flask server that serves model predictions
2. **Frontend Integration** (`UI/components/prediction-interface.tsx`) - Connected to real API
3. **Documentation** - Full guide in `UI/BACKEND_INTEGRATION.md`

---

## 🚀 Quick Test (2 Steps)

### Step 1: Start Backend
```bash
cd src
python api_server.py
```
**Expected output:**
```
============================================================
Spotify Song Mood Classifier API Server
============================================================
Audio model loaded: True
Lyrics classifier loaded: True

API Endpoints:
  GET  /api/health  - Health check
  POST /api/predict - Predict song mood

Starting server on http://localhost:8000
============================================================
```

### Step 2: Start Frontend
```bash
cd UI
npm run dev
# or
pnpm dev
```
**Open:** `http://localhost:3000`

---

## 🧪 Test It!

1. Navigate to the "Try the Classifier" section
2. Enter a song name: **"Happy"**
3. Click **"Predict"**
4. You should see real predictions!

---

## ⚠️ Troubleshooting

### Backend won't start?
- **Check:** Model file exists? (`models/new_song_mood_model.joblib`)
- **Fix:** Run `python src/train_from_mapped.py` first

### "Song not found" error?
- **Normal:** Song must exist in your dataset
- **Try:** Songs from your CSV files, or check `data/processed/` for available songs

### Frontend can't connect?
- **Check:** Backend running on port 8000?
- **Fix:** Start backend first, then frontend

### CORS errors?
- **Already fixed!** The backend has `CORS(app)` enabled

---

## 📋 API Endpoint Details

### POST `/api/predict`
**Request:**
```json
{
  "song": "Happy",
  "artist": "Pharrell Williams"  // optional
}
```

**Response:**
```json
{
  "song": "Happy",
  "artist": "Pharrell Williams",
  "audio": {
    "mood": "happy",
    "confidence": 0.75,
    "lowConfidence": false
  },
  "lyrics": {
    "mood": "happy",
    "confidence": 0.88,
    "lowConfidence": false
  },
  "agree": true
}
```

---

## 📝 Notes

- The backend **automatically searches** your dataset files for songs
- It looks in: `songs_balanced_sample.csv` → `songs_mapped.csv` → `songs_with_predictions.csv`
- Frontend supports **"Song Name by Artist"** format parsing
- Error handling is built-in for missing songs or models

---

## 🎯 What's Next?

The `PredictionInterface` component is now fully connected! Other components (model-comparison, uncertainty-analysis, etc.) still use static data - you can connect those later if needed.

For full details, see: `UI/BACKEND_INTEGRATION.md`

