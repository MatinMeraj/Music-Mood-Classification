"use client"

import { Card } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts"

const datasetDistribution = [
  { mood: "Happy", count: 214602, color: "hsl(var(--happy))" },
  { mood: "Chill", count: 27966, color: "hsl(var(--chill))" },
  { mood: "Sad", count: 171078, color: "hsl(var(--sad))" },
  { mood: "Hyped", count: 137777, color: "hsl(var(--hyped))" },
]

export function DatasetExplorer() {
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

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
          {datasetDistribution.map((item) => (
            <div key={item.mood} className="p-4 rounded-lg border border-border">
              <p className="text-sm text-muted-foreground mb-1">{item.mood}</p>
              <p className="text-2xl font-bold" style={{ color: item.color }}>
                {(item.count / 1000).toFixed(0)}K
              </p>
              <p className="text-xs text-muted-foreground mt-1">{((item.count / 551423) * 100).toFixed(1)}% of total</p>
            </div>
          ))}
        </div>

        <div className="mt-6 p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
          <h4 className="font-semibold text-sm text-yellow-700 mb-2">Class Imbalance Warning</h4>
          <p className="text-xs text-muted-foreground">
            The dataset shows significant imbalance with &quot;Chill&quot; having only 27,966 samples (5.1%) compared to
            &quot;Happy&quot; with 214,602 (38.9%). This imbalance may affect model performance and explains some
            prediction biases.
          </p>
        </div>
        <p className="text-center text-sm text-muted-foreground mt-4 font-medium">
          Figure 7: Balanced dataset distribution after sampling evenly from each mood class.
        </p>
      </Card>
    </section>
  )
}
