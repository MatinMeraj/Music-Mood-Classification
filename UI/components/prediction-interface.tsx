"use client"

import { useState } from "react"
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

export function PredictionInterface() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedSong, setSelectedSong] = useState<SongPrediction | null>(null)
  const [isSearching, setIsSearching] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async () => {
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
      
      const byMatch = searchQuery.match(/^(.+?)\s+by\s+(.+)$/i)
      if (byMatch) {
        songName = byMatch[1].trim()
        artistName = byMatch[2].trim()
      }
      
      const response = await fetch(`${API_BASE_URL}/api/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          song: songName,
          artist: artistName,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      
      // Convert API response to component format
      if (data.audio && data.lyrics) {
        setSelectedSong({
          song: data.song,
          artist: data.artist,
          audio: {
            mood: data.audio.mood,
            confidence: data.audio.confidence,
            lowConfidence: data.audio.lowConfidence,
          },
          lyrics: {
            mood: data.lyrics.mood,
            confidence: data.lyrics.confidence,
            lowConfidence: data.lyrics.lowConfidence,
          },
          agree: data.agree ?? false,
        })
      } else if (data.audio) {
        // Only audio prediction available
        setSelectedSong({
          song: data.song,
          artist: data.artist,
          audio: {
            mood: data.audio.mood,
            confidence: data.audio.confidence,
            lowConfidence: data.audio.lowConfidence,
          },
          lyrics: {
            mood: "happy", // Default
            confidence: 0,
            lowConfidence: true,
          },
          agree: false,
        })
        setError("Lyrics prediction not available for this song")
      } else {
        throw new Error("No predictions received from server")
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to get prediction"
      setError(errorMessage)
      console.error("Prediction error:", err)
      
      // Optionally fall back to sample songs on error
      if (errorMessage.includes("not found in dataset")) {
        setError(`${errorMessage}. Try one of the sample songs: Happy, Someone Like You, Lose Yourself`)
      }
    } finally {
      setIsSearching(false)
    }
  }

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
            <Button onClick={handleSearch} disabled={isSearching || !searchQuery.trim()}>
              {isSearching ? "Analyzing..." : "Predict"}
            </Button>
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
                {!selectedSong.agree && (
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
  const isLowConfidence = prediction.confidence < threshold

  return (
    <Card className="p-5 space-y-4">
      <h4 className="font-semibold text-sm text-muted-foreground">{title}</h4>

      <div className="space-y-3">
        <div
          className={cn(
            "inline-flex items-center gap-2 px-4 py-2 rounded-lg border-2 font-semibold text-lg capitalize",
            moodColors[prediction.mood],
          )}
        >
          {prediction.mood}
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Confidence</span>
            <span className="font-semibold">{(prediction.confidence * 100).toFixed(1)}%</span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div
              className={cn("h-full transition-all rounded-full", isLowConfidence ? "bg-yellow-500" : "bg-primary")}
              style={{ width: `${prediction.confidence * 100}%` }}
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
