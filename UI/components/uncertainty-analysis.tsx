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

interface LowConfidenceData {
  mood: string
  audio: number
  lyrics: number
}

interface ConfidenceDistribution {
  range: string
  audio: number
  lyrics: number
}

export function UncertaintyAnalysis() {
  const [lowConfidenceData, setLowConfidenceData] = useState<LowConfidenceData[]>([])
  const [confidenceDistribution, setConfidenceDistribution] = useState<ConfidenceDistribution[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const response = await fetch(`${API_BASE_URL}/api/stats`)
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        
        // Update low confidence data - ensure numeric values and filter invalid
        if (data.lowConfidence && Array.isArray(data.lowConfidence)) {
          const filtered = data.lowConfidence
            .filter((item: any) => item && typeof item === 'object' && item.mood)
            .map((item: LowConfidenceData) => {
              const audio = Number(item.audio)
              const lyrics = Number(item.lyrics)
              return {
                mood: String(item.mood || ""),
                audio: isNaN(audio) ? 0 : Math.max(0, Math.min(100, audio)),
                lyrics: isNaN(lyrics) ? 0 : Math.max(0, Math.min(100, lyrics)),
              }
            })
            .filter((item: LowConfidenceData) => item.mood && item.mood.length > 0)
          setLowConfidenceData(filtered.length > 0 ? filtered : [])
        }
        
        // Update confidence distribution - ensure numeric values and filter invalid
        if (data.confidenceDistribution && Array.isArray(data.confidenceDistribution)) {
          const filtered = data.confidenceDistribution
            .filter((item: any) => item && typeof item === 'object' && item.range)
            .map((item: ConfidenceDistribution) => ({
              range: String(item.range || ""),
              audio: isNaN(Number(item.audio)) ? 0 : Math.max(0, Number(item.audio)),
              lyrics: isNaN(Number(item.lyrics)) ? 0 : Math.max(0, Number(item.lyrics)),
            }))
            .filter((item: ConfidenceDistribution) => item.range && item.range.length > 0)
          setConfidenceDistribution(filtered.length > 0 ? filtered : [])
        }
        
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Failed to load statistics"
        setError(errorMessage)
        console.error("Error fetching stats:", err)
      } finally {
        setLoading(false)
      }
    }
    
    fetchStats()
  }, [])
  if (loading) {
    return (
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl sm:text-4xl font-bold text-balance">Uncertainty Analysis</h2>
          <p className="text-muted-foreground text-lg text-balance">
            Understanding model confidence and prediction uncertainty
          </p>
        </div>
        <Card className="p-6">
          <p className="text-center text-muted-foreground">Loading statistics...</p>
        </Card>
      </section>
    )
  }

  if (error) {
    return (
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl sm:text-4xl font-bold text-balance">Uncertainty Analysis</h2>
          <p className="text-muted-foreground text-lg text-balance">
            Understanding model confidence and prediction uncertainty
          </p>
        </div>
        <Card className="p-6">
          <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-sm">
            <p className="font-semibold mb-1">Error loading statistics</p>
            <p>{error}</p>
            <p className="mt-2 text-xs">Make sure the API server is running on {API_BASE_URL}</p>
          </div>
        </Card>
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
            {lowConfidenceData.length > 0 ? (
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
            ) : (
              <p className="text-center text-muted-foreground py-8">No low-confidence data available</p>
            )}
            {lowConfidenceData.length > 0 && (
              <>
                <div className="grid sm:grid-cols-2 gap-4 mt-6">
                  <div className="p-4 rounded-lg bg-hyped/10 border border-hyped/30">
                    <p className="text-sm font-semibold text-hyped mb-1">Audio Model Challenge</p>
                    <p className="text-xs text-muted-foreground">
                      {(() => {
                        const hypedItem = lowConfidenceData.find(d => d.mood === "Hyped")
                        const val = hypedItem?.audio ?? 0
                        return isFinite(val) ? val.toFixed(1) : "0.0"
                      })()}% low-confidence on "hyped" predictions
                    </p>
                  </div>
                  <div className="p-4 rounded-lg bg-chart-2/10 border border-chart-2/30">
                    <p className="text-sm font-semibold text-chart-2 mb-1">Lyrics Model Strength</p>
                    <p className="text-xs text-muted-foreground">Low-confidence rates typically &lt; 5% for most moods</p>
                  </div>
                </div>
                <p className="text-center text-sm text-muted-foreground mt-4 font-medium">
                  Figure 5: Low-confidence predictions by mood. Audio model struggles with &apos;hyped&apos; ({(() => {
                    const hypedItem = lowConfidenceData.find(d => d.mood === "Hyped")
                    const val = hypedItem?.audio ?? 0
                    return isFinite(val) ? val.toFixed(1) : "0.0"
                  })()}%
                  low-confidence).
                </p>
              </>
            )}
          </Card>
        </TabsContent>

        <TabsContent value="distribution" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-6">Confidence Score Distribution</h3>
            {confidenceDistribution.length > 0 ? (
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
            ) : (
              <p className="text-center text-muted-foreground py-8">No confidence distribution data available</p>
            )}
            <p className="text-center text-sm text-muted-foreground mt-4 font-medium">
              Figure 6: Confidence score distribution. Audio model confidence clusters in 0.2-0.6 range,
              while lyrics model shows high confidence with most predictions above 0.8.
            </p>
          </Card>
        </TabsContent>
      </Tabs>
    </section>
  )
}
