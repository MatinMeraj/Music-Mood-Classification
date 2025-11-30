"use client"

import { Card } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts"

interface DatasetDistribution {
  mood: string
  count: number
  color: string
}

export function DatasetExplorer() {
  // Hardcoded data from report: 20,000 songs, 5,000 per mood
  const moodColors: Record<string, string> = {
    "Happy": "hsl(var(--happy))",
    "Chill": "hsl(var(--chill))",
    "Sad": "hsl(var(--sad))",
    "Hyped": "hsl(var(--hyped))",
  }
  
  const datasetDistribution: DatasetDistribution[] = [
    { mood: "Happy", count: 5000, color: moodColors["Happy"] },
    { mood: "Chill", count: 5000, color: moodColors["Chill"] },
    { mood: "Sad", count: 5000, color: moodColors["Sad"] },
    { mood: "Hyped", count: 5000, color: moodColors["Hyped"] },
  ]
  const total = 20000

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
