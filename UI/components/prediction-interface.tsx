"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Search, Music, AlertCircle } from "lucide-react"
import { cn } from "@/lib/utils"

interface Prediction {
  mood: "happy" | "chill" | "sad" | "hyped"
  confidence: number
  lowConfidence: boolean
}

interface SongPrediction {
  song: string
  artist: string
  audio: Prediction
  lyrics: Prediction
  agree: boolean
}

const SAMPLE_SONGS: SongPrediction[] = [
  {
    song: "Happy",
    artist: "Pharrell Williams",
    audio: { mood: "happy", confidence: 0.82, lowConfidence: false },
    lyrics: { mood: "happy", confidence: 0.91, lowConfidence: false },
    agree: true,
  },
  {
    song: "Someone Like You",
    artist: "Adele",
    audio: { mood: "sad", confidence: 0.76, lowConfidence: false },
    lyrics: { mood: "sad", confidence: 0.88, lowConfidence: false },
    agree: true,
  },
  {
    song: "Lose Yourself",
    artist: "Eminem",
    audio: { mood: "hyped", confidence: 0.28, lowConfidence: true },
    lyrics: { mood: "sad", confidence: 0.65, lowConfidence: false },
    agree: false,
  },
  {
    song: "The Scientist",
    artist: "Coldplay",
    audio: { mood: "chill", confidence: 0.54, lowConfidence: false },
    lyrics: { mood: "sad", confidence: 0.79, lowConfidence: false },
    agree: false,
  },
]

const moodColors = {
  happy: "text-happy border-happy bg-happy/10",
  chill: "text-chill border-chill bg-chill/10",
  sad: "text-sad border-sad bg-sad/10",
  hyped: "text-hyped border-hyped bg-hyped/10",
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

console.log("PredictionInterface: Module loaded, API_BASE_URL:", API_BASE_URL)

export function PredictionInterface() {
  useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).testPredictionInterface = true
      console.log("PredictionInterface: Component mounted on CLIENT")
    }
  }, [])
  
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedSong, setSelectedSong] = useState<SongPrediction | null>(null)
  const [isSearching, setIsSearching] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async () => {
    console.log("PredictionInterface: handleSearch called with query:", searchQuery)
    if (!searchQuery.trim()) {
      setError("Please enter a song name")
      return
    }

    setIsSearching(true)
    setError(null)
    
    try {
      // Parse song name and optional artist from search query
      // Format: "Song Name" or "Song Name by Artist"
      let songName = searchQuery.trim()
      let artistName = "Unknown Artist"
      
      // Match "Song Name by Artist" - use greedy matching to get the last "by" (in case song name contains "by")
      const byMatch = searchQuery.match(/^(.+?)\s+by\s+(.+)$/i)
      if (byMatch) {
        songName = byMatch[1].trim()
        artistName = byMatch[2].trim()
      }
      
      // Validate parsed values
      if (!songName) {
        throw new Error("Song name cannot be empty")
      }
      if (!artistName || artistName === "Unknown Artist") {
        // If no artist specified, try to extract from song name or use default
        artistName = "Unknown Artist"
      }
      
      console.log("PredictionInterface: Making API call to", `${API_BASE_URL}/api/predict`, "with:", { song: songName, artist: artistName })
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 15000) // 15 second timeout
      
      let response: Response
      try {
        response = await fetch(`${API_BASE_URL}/api/predict`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            song: songName,
            artist: artistName,
          }),
          signal: controller.signal,
        })
      } finally {
        // Always clear timeout, even if fetch throws
        clearTimeout(timeoutId)
      }

      if (!response.ok) {
        // Try to parse error response, but handle non-JSON responses
        let errorMessage = `HTTP error! status: ${response.status}`
        try {
          const errorData = await response.json()
          errorMessage = errorData.error || errorMessage
        } catch {
          // Response is not JSON, use status text if available
          errorMessage = response.statusText || errorMessage
        }
        throw new Error(errorMessage)
      }

      const data = await response.json()
      
      // Validate response structure
      if (!data || typeof data !== 'object') {
        throw new Error("Invalid response format from server")
      }
      
      // Validate and convert API response to component format
      if (!data.song || !data.artist) {
        throw new Error("Response missing song or artist information")
      }
      
      // Validate audio prediction
      if (!data.audio || !data.audio.mood || typeof data.audio.confidence !== 'number' || !Number.isFinite(data.audio.confidence)) {
        throw new Error("Invalid audio prediction in response")
      }
      
      // Validate mood is one of the expected values
      const validMoods = ['happy', 'chill', 'sad', 'hyped']
      if (!validMoods.includes(data.audio.mood.toLowerCase())) {
        throw new Error(`Invalid mood value: ${data.audio.mood}`)
      }
      
      // Check if lyrics prediction exists (not null or undefined)
      if (data.audio && data.lyrics !== null && data.lyrics !== undefined) {
        // Validate lyrics prediction
        if (!data.lyrics.mood || typeof data.lyrics.confidence !== 'number' || !Number.isFinite(data.lyrics.confidence)) {
          throw new Error("Invalid lyrics prediction in response")
        }
        if (!validMoods.includes(data.lyrics.mood.toLowerCase())) {
          throw new Error(`Invalid lyrics mood value: ${data.lyrics.mood}`)
        }
        
        setSelectedSong({
          song: data.song,
          artist: data.artist,
          audio: {
            mood: data.audio.mood.toLowerCase() as "happy" | "chill" | "sad" | "hyped",
            confidence: Math.max(0, Math.min(1, data.audio.confidence)), // Clamp between 0 and 1
            lowConfidence: data.audio.lowConfidence ?? false,
          },
          lyrics: {
            mood: data.lyrics.mood.toLowerCase() as "happy" | "chill" | "sad" | "hyped",
            confidence: Math.max(0, Math.min(1, data.lyrics.confidence)), // Clamp between 0 and 1
            lowConfidence: data.lyrics.lowConfidence ?? false,
          },
          // Handle agree: can be boolean or null (when lyrics is missing)
          agree: data.agree === null || data.agree === undefined ? false : Boolean(data.agree),
        })
      } else if (data.audio) {
        // Only audio prediction available (lyrics is null or missing)
        setSelectedSong({
          song: data.song,
          artist: data.artist,
          audio: {
            mood: data.audio.mood.toLowerCase() as "happy" | "chill" | "sad" | "hyped",
            confidence: Math.max(0, Math.min(1, data.audio.confidence)), // Clamp between 0 and 1
            lowConfidence: data.audio.lowConfidence ?? false,
          },
          lyrics: {
            mood: "happy", // Default fallback
            confidence: 0,
            lowConfidence: true,
          },
          // When lyrics is missing, agree should be false (models can't agree if one is missing)
          agree: false,
        })
        // Only show error if lyrics was explicitly null (not just missing)
        // This allows the UI to still display the audio prediction
        if (data.lyrics === null) {
          setError("Lyrics prediction not available for this song")
        }
      } else {
        throw new Error("No predictions received from server")
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to get prediction"
      console.error("Prediction error:", err)
      
      // Provide helpful error messages
      if (errorMessage.includes("Failed to fetch") || errorMessage.includes("aborted")) {
        setError(`API server not available. Please start the API server: python src/api_server.py`)
      } else if (errorMessage.includes("not found in dataset")) {
        setError(`${errorMessage}. Try one of the sample songs: Happy, Someone Like You, Lose Yourself`)
      } else {
        setError(errorMessage)
      }
    } finally {
      setIsSearching(false)
    }
  }
  
  // Expose handleSearch globally for the test button
  useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).__triggerPredict__ = () => {
        console.log("PredictionInterface: Global predict function called, searchQuery:", searchQuery)
        if (searchQuery.trim()) {
          handleSearch()
        } else {
          const input = document.querySelector('input[placeholder*="Search for a song"]') as HTMLInputElement
          if (input && input.value.trim()) {
            // Use the same parsing logic as handleSearch
            const query = input.value.trim()
            let songName = query
            let artistName = "Unknown Artist"
            const byMatch = query.match(/^(.+?)\s+by\s+(.+)$/i)
            if (byMatch) {
              songName = byMatch[1].trim()
              artistName = byMatch[2].trim()
            }
            
            // Validate before making API call
            if (!songName) {
              alert("Error: Song name cannot be empty")
              return
            }
            
            // Make direct API call with proper error handling
            fetch(`${API_BASE_URL}/api/predict`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ song: songName, artist: artistName }),
            })
            .then(async r => {
              if (!r.ok) {
                let errorMsg = `HTTP error! status: ${r.status}`
                try {
                  const errorData = await r.json()
                  errorMsg = errorData.error || errorMsg
                } catch {
                  errorMsg = r.statusText || errorMsg
                }
                throw new Error(errorMsg)
              }
              return r.json()
            })
            .then(data => {
              console.log("Predict response:", data)
              alert("Prediction: " + JSON.stringify(data, null, 2))
            })
            .catch(err => {
              console.error("Predict error:", err)
              alert("Error: " + (err instanceof Error ? err.message : String(err)))
            })
          } else {
            alert("Please enter a song name first")
          }
        }
      }
    }
  }, [searchQuery, handleSearch])

  return (
    <section id="try" className="py-16 bg-muted/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-4 mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-balance">Try the Classifier</h2>
          <p className="text-muted-foreground text-lg text-balance">
            Enter a song name to see mood predictions from both models
          </p>
        </div>

        <Card className="p-6 max-w-4xl mx-auto space-y-6">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <Input
                placeholder="Search for a song or try: Happy, Someone Like You, Lose Yourself..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                className="pl-10"
              />
            </div>
            <div>
              <Button 
                onClick={(e) => {
                  console.log("PredictionInterface: Button clicked!", { searchQuery, isSearching })
                  e.preventDefault()
                  handleSearch()
                }} 
                disabled={isSearching || !searchQuery.trim()}
              >
                {isSearching ? "Analyzing..." : "Predict"}
              </Button>
              <button
                onClick={() => {
                  console.log("Test button clicked!")
                  if ((window as any).__triggerPredict__) {
                    (window as any).__triggerPredict__()
                  } else {
                    alert("React handler not ready. Trying direct API call...")
                    const input = document.querySelector('input[placeholder*="Search for a song"]') as HTMLInputElement
                    if (input && input.value.trim()) {
                      const query = input.value.trim()
                      let songName = query
                      let artistName = "Unknown Artist"
                      const byMatch = query.match(/^(.+?)\s+by\s+(.+)$/i)
                      if (byMatch) {
                        songName = byMatch[1].trim()
                        artistName = byMatch[2].trim()
                      }
                      
                      if (!songName) {
                        alert("Error: Song name cannot be empty")
                        return
                      }
                      
                      fetch(`${API_BASE_URL}/api/predict`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ song: songName, artist: artistName })
                      })
                      .then(async r => {
                        if (!r.ok) {
                          let errorMsg = `HTTP error! status: ${r.status}`
                          try {
                            const errorData = await r.json()
                            errorMsg = errorData.error || errorMsg
                          } catch {
                            errorMsg = r.statusText || errorMsg
                          }
                          throw new Error(errorMsg)
                        }
                        return r.json()
                      })
                      .then(data => {
                        console.log("Predict response:", data)
                        alert("Prediction: " + JSON.stringify(data, null, 2))
                      })
                      .catch(err => {
                        console.error("Predict error:", err)
                        alert("Error: " + (err instanceof Error ? err.message : String(err)))
                      })
                    } else {
                      alert("Please enter a song name first")
                    }
                  }
                }}
                style={{ marginLeft: '10px', padding: '10px', backgroundColor: 'green', color: 'white', border: 'none', cursor: 'pointer' }}
              >
                Test Predict (Plain HTML)
              </button>
            </div>
          </div>

          {error && (
            <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-sm">
              {error}
            </div>
          )}

          {selectedSong && (
            <div className="space-y-6 pt-4">
              <div className="flex items-center gap-3 pb-4 border-b border-border">
                <Music className="w-6 h-6 text-primary" />
                <div>
                  <h3 className="font-semibold text-lg">{selectedSong.song}</h3>
                  <p className="text-sm text-muted-foreground">{selectedSong.artist}</p>
                </div>
                {selectedSong.agree === false && (
                  <Badge variant="outline" className="ml-auto border-yellow-500 text-yellow-500">
                    Models Disagree
                  </Badge>
                )}
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <PredictionCard
                  title="Main Method - Audio Classifier"
                  prediction={selectedSong.audio}
                  threshold={0.35}
                  features={[
                    "Tempo",
                    "Energy",
                    "Valence",
                    "Loudness",
                    "Danceability",
                    "Speechiness",
                    "Acousticness",
                    "Instrumentalness",
                    "Liveness",
                  ]}
                />
                <PredictionCard
                  title="Baseline Comparison - Lyrics Classifier"
                  prediction={selectedSong.lyrics}
                  threshold={0.6}
                  description="VADER Sentiment Analysis (Not Trained)"
                />
              </div>
            </div>
          )}
        </Card>
      </div>
    </section>
  )
}

function PredictionCard({
  title,
  prediction,
  threshold,
  features,
  description,
}: {
  title: string
  prediction: Prediction
  threshold: number
  features?: string[]
  description?: string
}) {
  // Validate prediction data
  if (!prediction || typeof prediction.confidence !== 'number' || !Number.isFinite(prediction.confidence)) {
    console.warn("PredictionCard: Invalid prediction data", prediction)
    return (
      <Card className="p-5 space-y-4">
        <h4 className="font-semibold text-sm text-muted-foreground">{title}</h4>
        <p className="text-sm text-destructive">Invalid prediction data</p>
      </Card>
    )
  }
  
  const isLowConfidence = prediction.confidence < threshold

  return (
    <Card className="p-5 space-y-4">
      <h4 className="font-semibold text-sm text-muted-foreground">{title}</h4>

      <div className="space-y-3">
        <div
          className={cn(
            "inline-flex items-center gap-2 px-4 py-2 rounded-lg border-2 font-semibold text-lg capitalize",
            moodColors[prediction.mood as keyof typeof moodColors] || moodColors.happy, // Fallback to happy if mood not found
          )}
        >
          {prediction.mood}
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Confidence</span>
            <span className="font-semibold">
              {Number.isFinite(prediction.confidence) 
                ? (Math.max(0, Math.min(1, prediction.confidence)) * 100).toFixed(1)
                : '0.0'}%
            </span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div
              className={cn("h-full transition-all rounded-full", isLowConfidence ? "bg-yellow-500" : "bg-primary")}
              style={{ 
                width: `${Math.max(0, Math.min(100, (Number.isFinite(prediction.confidence) ? prediction.confidence : 0) * 100))}%` 
              }}
            />
          </div>
        </div>

        {isLowConfidence && (
          <div className="flex items-start gap-2 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
            <AlertCircle className="w-4 h-4 text-yellow-700 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-yellow-700">Low confidence prediction (&lt; {threshold * 100}%)</p>
          </div>
        )}

        {features && (
          <div className="pt-2 border-t border-border">
            <p className="text-xs font-medium text-muted-foreground mb-2">Features Used:</p>
            <div className="flex flex-wrap gap-1">
              {features.map((feature) => (
                <Badge key={feature} variant="secondary" className="text-[10px]">
                  {feature}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {description && (
          <div className="pt-2 border-t border-border">
            <p className="text-xs text-muted-foreground">{description}</p>
          </div>
        )}
      </div>
    </Card>
  )
}
