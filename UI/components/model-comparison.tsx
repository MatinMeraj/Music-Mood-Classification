"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface AgreementData {
  name: string
  value: number
  color: string
}

interface DistributionData {
  mood: string
  audio: number
  lyrics: number
}

interface ConfusionData {
  audio: string
  happy: number
  chill: number
  sad: number
  hyped: number
}

export function ModelComparison() {
  const [agreementData, setAgreementData] = useState<AgreementData[]>([
    { name: "Agree", value: 0, color: "hsl(var(--chart-2))" },
    { name: "Disagree", value: 0, color: "hsl(var(--chart-4))" },
  ])
  const [distributionData, setDistributionData] = useState<DistributionData[]>([])
  const [confusionData, setConfusionData] = useState<ConfusionData[]>([])
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
        
        // Update agreement data - ensure valid numbers
        if (data.agreement && typeof data.agreement === 'object') {
          const agreePct = Number(data.agreement.agree_pct)
          const disagreePct = Number(data.agreement.disagree_pct)
          setAgreementData([
            { 
              name: "Agree", 
              value: isNaN(agreePct) ? 0 : Math.max(0, Math.min(100, agreePct)), 
              color: "hsl(var(--chart-2))" 
            },
            { 
              name: "Disagree", 
              value: isNaN(disagreePct) ? 0 : Math.max(0, Math.min(100, disagreePct)), 
              color: "hsl(var(--chart-4))" 
            },
          ])
        }
        
        // Update distribution data - ensure numeric values and filter invalid
        if (data.distribution && Array.isArray(data.distribution)) {
          const filtered = data.distribution
            .filter((item: any) => item && typeof item === 'object' && item.mood)
            .map((item: DistributionData) => {
              const audio = Number(item.audio)
              const lyrics = Number(item.lyrics)
              return {
                mood: String(item.mood || ""),
                audio: isNaN(audio) ? 0 : Math.max(0, audio),
                lyrics: isNaN(lyrics) ? 0 : Math.max(0, lyrics),
              }
            })
            .filter((item: DistributionData) => item.mood && item.mood.length > 0)
          setDistributionData(filtered.length > 0 ? filtered : [])
        }
        
        // Update confusion matrix - ensure numeric values and filter invalid
        if (data.confusion && Array.isArray(data.confusion)) {
          const filtered = data.confusion
            .filter((item: any) => item && typeof item === 'object' && item.audio)
            .map((item: ConfusionData) => ({
              audio: String(item.audio || ""),
              happy: isNaN(Number(item.happy)) ? 0 : Math.max(0, Number(item.happy)),
              chill: isNaN(Number(item.chill)) ? 0 : Math.max(0, Number(item.chill)),
              sad: isNaN(Number(item.sad)) ? 0 : Math.max(0, Number(item.sad)),
              hyped: isNaN(Number(item.hyped)) ? 0 : Math.max(0, Number(item.hyped)),
            }))
            .filter((item: ConfusionData) => item.audio && item.audio.length > 0)
          setConfusionData(filtered.length > 0 ? filtered : [])
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
          <h2 className="text-3xl sm:text-4xl font-bold text-balance">Model Comparison</h2>
          <p className="text-muted-foreground text-lg text-balance">
            How audio and lyrics models compare in their predictions
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
          <h2 className="text-3xl sm:text-4xl font-bold text-balance">Model Comparison</h2>
          <p className="text-muted-foreground text-lg text-balance">
            How audio and lyrics models compare in their predictions
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

  // Calculate threshold for confusion matrix highlighting (75th percentile)
  const allValues = confusionData.length > 0
    ? confusionData.flatMap(row => [
        Number(row.happy) || 0,
        Number(row.chill) || 0,
        Number(row.sad) || 0,
        Number(row.hyped) || 0
      ]).filter(v => isFinite(v) && v > 0)
    : []
  const threshold = allValues.length > 0 
    ? (() => {
        const sorted = allValues.sort((a, b) => b - a)
        const idx = Math.floor(allValues.length * 0.25)
        const val = sorted[idx]
        return isFinite(val) && val >= 0 ? val : 0
      })()
    : 0

  return (
    <section className="space-y-8">
      <div className="text-center space-y-4">
        <h2 className="text-3xl sm:text-4xl font-bold text-balance">Model Comparison</h2>
        <p className="text-muted-foreground text-lg text-balance">
          How audio and lyrics models compare in their predictions
        </p>
      </div>

      <Tabs defaultValue="agreement" className="space-y-6">
        <TabsList className="grid w-full max-w-md mx-auto grid-cols-3">
          <TabsTrigger value="agreement">Agreement</TabsTrigger>
          <TabsTrigger value="distribution">Distribution</TabsTrigger>
          <TabsTrigger value="confusion">Confusion</TabsTrigger>
        </TabsList>

        <TabsContent value="agreement" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-6">Overall Model Agreement</h3>
            {agreementData.length > 0 && agreementData.some(d => d.value > 0) ? (
              <>
                <ResponsiveContainer width="100%" height={400}>
                  <PieChart>
                    <Pie
                      data={agreementData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => {
                        const val = Number(value) || 0
                        return isFinite(val) ? `${name}: ${val.toFixed(1)}%` : `${name}: 0.0%`
                      }}
                      outerRadius={120}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {agreementData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <p className="text-center text-sm text-muted-foreground mt-4 font-medium">
                  Figure 2: Agreement between main method (audio) and baseline (lyrics). {agreementData[1] && isFinite(agreementData[1].value) ? agreementData[1].value.toFixed(1) : '0.0'}% disagreement highlights
                  complementary strengths.
                </p>
              </>
            ) : (
              <p className="text-center text-muted-foreground py-8">No agreement data available</p>
            )}
          </Card>
        </TabsContent>

        <TabsContent value="distribution" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-6">Prediction Distribution by Model</h3>
            {distributionData.length > 0 ? (
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={distributionData}>
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
                    value: "Percentage (%)",
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
                <Legend wrapperStyle={{ color: "hsl(var(--foreground))" }} iconType="rect" />
                  <Bar dataKey="audio" name="Audio Model" fill="hsl(var(--chart-1))" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="lyrics" name="Lyrics Model" fill="hsl(var(--chart-3))" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-center text-muted-foreground py-8">No distribution data available</p>
            )}
            <p className="text-center text-sm text-muted-foreground mt-4 font-medium">
              Figure 3: Prediction distribution comparing main method (audio) vs baseline (lyrics) predictions.
            </p>
          </Card>
        </TabsContent>

        <TabsContent value="confusion" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-6">Audio vs Lyrics Confusion Matrix</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="p-3 text-left font-semibold">Audio ↓ / Lyrics →</th>
                    <th className="p-3 text-center font-semibold text-happy">Happy</th>
                    <th className="p-3 text-center font-semibold text-chill">Chill</th>
                    <th className="p-3 text-center font-semibold text-sad">Sad</th>
                    <th className="p-3 text-center font-semibold text-hyped">Hyped</th>
                  </tr>
                </thead>
                <tbody>
                  {confusionData.length > 0 ? (
                    confusionData.map((row, i) => (
                      <tr key={i} className="border-b border-border/50">
                        <td className="p-3 font-semibold">{row.audio}</td>
                        <td className="p-3 text-center">
                          <span className={(Number(row.happy) || 0) > threshold ? "font-bold text-happy" : ""}>
                            {Number(row.happy) || 0}
                          </span>
                        </td>
                        <td className="p-3 text-center">
                          <span className={(Number(row.chill) || 0) > threshold ? "font-bold text-chill" : ""}>
                            {Number(row.chill) || 0}
                          </span>
                        </td>
                        <td className="p-3 text-center">
                          <span className={(Number(row.sad) || 0) > threshold ? "font-bold text-sad" : ""}>
                            {Number(row.sad) || 0}
                          </span>
                        </td>
                        <td className="p-3 text-center">
                          <span className={(Number(row.hyped) || 0) > threshold ? "font-bold text-hyped" : ""}>
                            {Number(row.hyped) || 0}
                          </span>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={5} className="p-8 text-center text-muted-foreground">
                        No confusion matrix data available
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            <p className="text-center text-sm text-muted-foreground mt-4 font-medium">
              Figure 4: Confusion matrix comparing main method (audio) vs baseline (lyrics) predictions.
            </p>
          </Card>
        </TabsContent>
      </Tabs>
    </section>
  )
}
