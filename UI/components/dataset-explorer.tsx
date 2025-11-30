"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface DatasetDistribution {
  mood: string
  count: number
  color: string
}

export function DatasetExplorer() {
  const [datasetDistribution, setDatasetDistribution] = useState<DatasetDistribution[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchDataset = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const response = await fetch(`${API_BASE_URL}/api/dataset`)
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        
        // Map API response to component format - ensure valid data
        if (data.distribution && Array.isArray(data.distribution)) {
          const moodColors: Record<string, string> = {
            "Happy": "hsl(var(--happy))",
            "Chill": "hsl(var(--chill))",
            "Sad": "hsl(var(--sad))",
            "Hyped": "hsl(var(--hyped))",
          }
          
          const mapped = data.distribution
            .filter((item: any) => item && typeof item === 'object' && item.mood)
            .map((item: { mood: string; count: number }) => {
              const count = Number(item.count)
              return {
                mood: String(item.mood || ""),
                count: isNaN(count) ? 0 : Math.max(0, count),
                color: moodColors[String(item.mood || "")] || "hsl(var(--muted-foreground))",
              }
            })
            .filter((item: DatasetDistribution) => item.mood && item.mood.length > 0)
          
          setDatasetDistribution(mapped.length > 0 ? mapped : [])
          setTotal(isNaN(Number(data.total)) ? 0 : Math.max(0, Number(data.total)))
        }
        
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Failed to load dataset statistics"
        setError(errorMessage)
        console.error("Error fetching dataset:", err)
      } finally {
        setLoading(false)
      }
    }
    
    fetchDataset()
  }, [])
  if (loading) {
    return (
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl sm:text-4xl font-bold text-balance">Dataset Overview</h2>
          <p className="text-muted-foreground text-lg text-balance">
            Understanding the distribution and balance of our training data
          </p>
        </div>
        <Card className="p-6">
          <p className="text-center text-muted-foreground">Loading dataset statistics...</p>
        </Card>
      </section>
    )
  }

  if (error) {
    return (
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl sm:text-4xl font-bold text-balance">Dataset Overview</h2>
          <p className="text-muted-foreground text-lg text-balance">
            Understanding the distribution and balance of our training data
          </p>
        </div>
        <Card className="p-6">
          <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-sm">
            <p className="font-semibold mb-1">Error loading dataset statistics</p>
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
        <h2 className="text-3xl sm:text-4xl font-bold text-balance">Dataset Overview</h2>
        <p className="text-muted-foreground text-lg text-balance">
          Understanding the distribution and balance of our training data
        </p>
      </div>

      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-6">Mood Class Distribution</h3>
        {datasetDistribution.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={datasetDistribution}>
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
                value: "Song Count",
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
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {datasetDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-center text-muted-foreground py-8">No dataset distribution data available</p>
        )}

        {datasetDistribution.length > 0 && total > 0 && (
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
            {datasetDistribution.map((item) => (
              <div key={item.mood} className="p-4 rounded-lg border border-border">
                <p className="text-sm text-muted-foreground mb-1">{item.mood}</p>
                <p className="text-2xl font-bold" style={{ color: item.color }}>
                  {(() => {
                    const count = Number(item.count) || 0
                    if (!isFinite(count) || count < 0) return "0"
                    return count >= 1000 ? `${(count / 1000).toFixed(0)}K` : count.toLocaleString()
                  })()}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {(() => {
                    const count = Number(item.count) || 0
                    const tot = Number(total) || 0
                    if (tot > 0 && isFinite(count) && count >= 0) {
                      const pct = (count / tot) * 100
                      return isFinite(pct) ? pct.toFixed(1) : "0.0"
                    }
                    return "0.0"
                  })()}% of total
                </p>
              </div>
            ))}
          </div>
        )}

        {datasetDistribution.length > 0 && total > 0 && (() => {
          const chillItem = datasetDistribution.find(d => d.mood === "Chill")
          const happyItem = datasetDistribution.find(d => d.mood === "Happy")
          const chillCount = chillItem ? (Number(chillItem.count) || 0) : 0
          const happyCount = happyItem ? (Number(happyItem.count) || 0) : 0
          const tot = Number(total) || 0
          
          const chillPct = tot > 0 && isFinite(chillCount) ? (chillCount / tot * 100) : 0
          const happyPct = tot > 0 && isFinite(happyCount) ? (happyCount / tot * 100) : 0
          
          if (isFinite(chillPct) && isFinite(happyPct) && (chillPct < 10 || happyPct > 30)) {
            return (
              <div className="mt-6 p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                <h4 className="font-semibold text-sm text-yellow-700 mb-2">Class Imbalance Warning</h4>
                <p className="text-xs text-muted-foreground">
                  The dataset shows significant imbalance with &quot;Chill&quot; having {chillPct.toFixed(1)}% of samples compared to
                  &quot;Happy&quot; with {happyPct.toFixed(1)}%. This imbalance may affect model performance and explains some
                  prediction biases.
                </p>
              </div>
            )
          }
          return null
        })()}
        <p className="text-center text-sm text-muted-foreground mt-4 font-medium">
          Figure 7: Balanced dataset distribution after sampling evenly from each mood class.
        </p>
      </Card>
    </section>
  )
}
