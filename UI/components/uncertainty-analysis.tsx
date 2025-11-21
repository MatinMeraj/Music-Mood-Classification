"use client"

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

const lowConfidenceData = [
  { mood: "Happy", audio: 26.5, lyrics: 1.7 },
  { mood: "Chill", audio: 33.3, lyrics: 30.6 },
  { mood: "Sad", audio: 14.4, lyrics: 4.3 },
  { mood: "Hyped", audio: 79.8, lyrics: 2.1 },
]

const confidenceDistribution = [
  { range: "0-0.2", audio: 0, lyrics: 0 },
  { range: "0.2-0.4", audio: 2406, lyrics: 26 },
  { range: "0.4-0.6", audio: 2594, lyrics: 169 },
  { range: "0.6-0.8", audio: 0, lyrics: 301 },
  { range: "0.8-1.0", audio: 0, lyrics: 4504 },
]

export function UncertaintyAnalysis() {
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
                <p className="text-xs text-muted-foreground">79.8% low-confidence on "hyped" predictions (only 28 correct out of 84)</p>
              </div>
              <div className="p-4 rounded-lg bg-chart-2/10 border border-chart-2/30">
                <p className="text-sm font-semibold text-chart-2 mb-1">Lyrics Model Strength</p>
                <p className="text-xs text-muted-foreground">Mean confidence 0.920 vs audio 0.403, with low-confidence rates &lt; 5% for most moods</p>
              </div>
            </div>
            <p className="text-center text-sm text-muted-foreground mt-4 font-medium">
              Figure 5: Low-confidence predictions by mood. Audio model struggles with &apos;hyped&apos; (79.8%
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
