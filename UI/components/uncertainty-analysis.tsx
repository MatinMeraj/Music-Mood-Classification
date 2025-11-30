"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

const defaultLowConfidenceData = [
  { mood: "Happy", audio: 0, lyrics: 0 },
  { mood: "Chill", audio: 0, lyrics: 0 },
  { mood: "Sad", audio: 0, lyrics: 0 },
  { mood: "Hyped", audio: 0, lyrics: 0 },
]

const defaultConfidenceDistribution = [
  { range: "0-0.2", audio: 0, lyrics: 0 },
  { range: "0.2-0.4", audio: 0, lyrics: 0 },
  { range: "0.4-0.6", audio: 0, lyrics: 0 },
  { range: "0.6-0.8", audio: 0, lyrics: 0 },
  { range: "0.8-1.0", audio: 0, lyrics: 0 },
]

export function UncertaintyAnalysis() {
  const [lowConfidenceData, setLowConfidenceData] = useState(defaultLowConfidenceData)
  const [confidenceDistribution, setConfidenceDistribution] = useState(defaultConfidenceDistribution)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Listen for custom event from inline script
    const handleStatsLoaded = (event: any) => {
      const data = event.detail
      console.log("UncertaintyAnalysis: Received stats from custom event:", data)
      
      // Handle both lowercase and camelCase
      const lowConf = data.lowConfidence || data.LowConfidence
      const confDist = data.confidenceDistribution || data.ConfidenceDistribution
      
      if (lowConf && lowConf.length > 0) {
        setLowConfidenceData(lowConf)
      }
      
      if (confDist && confDist.length > 0) {
        setConfidenceDistribution(confDist)
      }
      
      setError(null)
      setLoading(false)
    }

    // Register listener with global API data handler
    const handleData = (type: string, data: any) => {
      if (type === 'stats') {
        // Handle both lowercase and camelCase
        const lowConf = data.lowConfidence || data.LowConfidence
        const confDist = data.confidenceDistribution || data.ConfidenceDistribution
        
        if (lowConf && lowConf.length > 0) {
          setLowConfidenceData(lowConf)
        }
        
        if (confDist && confDist.length > 0) {
          setConfidenceDistribution(confDist)
        }
        
        setError(null)
        setLoading(false)
      }
    }

    // Register listener
    if (typeof window !== 'undefined' && (window as any).__registerAPIListener__) {
      (window as any).__registerAPIListener__(handleData)
      console.log("UncertaintyAnalysis: Registered API listener")
    }
    
    // Also listen for events
    const handleEvent = (event: any) => {
      handleData('stats', event.detail)
    }
    window.addEventListener('api-stats-loaded', handleEvent as EventListener)
    
    // Also try direct fetch as fallback
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/stats`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()
        
        if (data.lowConfidence && data.lowConfidence.length > 0) {
          setLowConfidenceData(data.lowConfidence)
        }
        
        if (data.confidenceDistribution && data.confidenceDistribution.length > 0) {
          setConfidenceDistribution(data.confidenceDistribution)
        }
        
        setError(null)
      } catch (err) {
        console.error("Error fetching stats:", err)
        const errorMessage = err instanceof Error ? err.message : "Failed to load statistics"
        if (errorMessage.includes("Failed to fetch") || errorMessage.includes("aborted")) {
          setError(`API server not available. Please start the API server: python src/api_server.py`)
        } else {
          setError(errorMessage)
        }
      } finally {
        setLoading(false)
      }
    }

    // Try fetch after a delay
    const timeoutId = setTimeout(() => {
      console.log("UncertaintyAnalysis: Attempting direct fetch...")
      fetchStats()
    }, 500)
    
    // Poll for global data
    const pollInterval = setInterval(() => {
      if (typeof window !== 'undefined' && (window as any).__API_DATA__?.stats) {
        const data = (window as any).__API_DATA__.stats
        console.log("UncertaintyAnalysis: Found data in global store, updating...")
        handleData('stats', data)
        clearInterval(pollInterval)
      }
    }, 500)

    return () => {
      window.removeEventListener('api-stats-loaded', handleEvent as EventListener)
      clearTimeout(timeoutId)
      clearInterval(pollInterval)
    }
  }, [])
  
  if (loading) {
    return (
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl sm:text-4xl font-bold text-balance">Uncertainty Analysis</h2>
          <p className="text-muted-foreground text-lg text-balance">
            Loading statistics...
          </p>
        </div>
      </section>
    )
  }

  if (error) {
    return (
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl sm:text-4xl font-bold text-balance">Uncertainty Analysis</h2>
          <p className="text-destructive text-lg">
            Error: {error}
          </p>
          <p className="text-muted-foreground text-sm">
            Make sure the API server is running on {API_BASE_URL}
          </p>
        </div>
      </section>
    )
  }

  return (
    <section className="space-y-8">
      <div className="text-center space-y-4">
        <h2 className="text-3xl sm:text-4xl font-bold text-balance">Uncertainty Analysis</h2>
        <p className="text-muted-foreground text-lg text-balance">
          Understanding model confidence and prediction uncertainty
        </p>
      </div>

      <Tabs defaultValue="low-confidence" className="space-y-6">
        <TabsList className="grid w-full max-w-md mx-auto grid-cols-2">
          <TabsTrigger value="low-confidence">Low Confidence</TabsTrigger>
          <TabsTrigger value="distribution">Distribution</TabsTrigger>
        </TabsList>

        <TabsContent value="low-confidence" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-6">Low-Confidence Predictions by Mood</h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={lowConfidenceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--muted-foreground))" opacity={0.5} />
                <XAxis
                  dataKey="mood"
                  stroke="hsl(var(--foreground))"
                  tick={{ fill: "hsl(var(--foreground))", fontSize: 14 }}
                />
                <YAxis
                  stroke="hsl(var(--foreground))"
                  tick={{ fill: "hsl(var(--foreground))", fontSize: 14 }}
                  label={{
                    value: "Low Confidence %",
                    angle: -90,
                    position: "insideLeft",
                    fill: "hsl(var(--foreground))",
                    style: { fontSize: 14 },
                  }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--popover))",
                    border: "1px solid hsl(var(--border))",
                    color: "hsl(var(--popover-foreground))",
                  }}
                  labelStyle={{ color: "hsl(var(--popover-foreground))" }}
                />
                <Legend iconType="rect" />
                <Bar dataKey="audio" name="Audio Model (<0.35)" fill="hsl(var(--chart-1))" radius={[4, 4, 0, 0]} />
                <Bar dataKey="lyrics" name="Lyrics Model (<0.60)" fill="hsl(var(--chart-3))" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            <div className="grid sm:grid-cols-2 gap-4 mt-6">
              <div className="p-4 rounded-lg bg-hyped/10 border border-hyped/30">
                <p className="text-sm font-semibold text-hyped mb-1">Audio Model Challenge</p>
                <p className="text-xs text-muted-foreground">
                  {lowConfidenceData.find(d => d.mood === "Hyped")?.audio.toFixed(1) || "0"}% low-confidence on "hyped" predictions
                </p>
              </div>
              <div className="p-4 rounded-lg bg-chart-2/10 border border-chart-2/30">
                <p className="text-sm font-semibold text-chart-2 mb-1">Lyrics Model Strength</p>
                <p className="text-xs text-muted-foreground">Mean confidence 0.920 vs audio 0.403, with low-confidence rates &lt; 5% for most moods</p>
              </div>
            </div>
            <p className="text-center text-sm text-muted-foreground mt-4 font-medium">
              Figure 5: Low-confidence predictions by mood. Audio model struggles with &apos;hyped&apos; ({lowConfidenceData.find(d => d.mood === "Hyped")?.audio.toFixed(1) || "0"}%
              low-confidence).
            </p>
          </Card>
        </TabsContent>

        <TabsContent value="distribution" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-6">Confidence Score Distribution</h3>
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={confidenceDistribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--muted-foreground))" opacity={0.5} />
                <XAxis
                  dataKey="range"
                  stroke="hsl(var(--foreground))"
                  tick={{ fill: "hsl(var(--foreground))", fontSize: 14 }}
                  label={{
                    value: "Confidence Range",
                    position: "insideBottom",
                    offset: -5,
                    fill: "hsl(var(--foreground))",
                    style: { fontSize: 14 },
                  }}
                />
                <YAxis
                  stroke="hsl(var(--foreground))"
                  tick={{ fill: "hsl(var(--foreground))", fontSize: 14 }}
                  label={{
                    value: "Count",
                    angle: -90,
                    position: "insideLeft",
                    fill: "hsl(var(--foreground))",
                    style: { fontSize: 14 },
                  }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--popover))",
                    border: "1px solid hsl(var(--border))",
                    color: "hsl(var(--popover-foreground))",
                  }}
                  labelStyle={{ color: "hsl(var(--popover-foreground))" }}
                />
                <Legend iconType="rect" />
                <Area
                  type="monotone"
                  dataKey="audio"
                  name="Audio Model"
                  stroke="hsl(var(--chart-1))"
                  fill="hsl(var(--chart-1))"
                  fillOpacity={0.7}
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="lyrics"
                  name="Lyrics Model"
                  stroke="hsl(var(--chart-3))"
                  fill="hsl(var(--chart-3))"
                  fillOpacity={0.7}
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
            <p className="text-center text-sm text-muted-foreground mt-4 font-medium">
              Figure 6: Confidence score distribution. Audio model confidence clusters in 0.2-0.6 range (mean: 0.403),
              while lyrics model shows high confidence (mean: 0.920) with 90% of predictions above 0.8.
            </p>
          </Card>
        </TabsContent>
      </Tabs>
    </section>
  )
}
