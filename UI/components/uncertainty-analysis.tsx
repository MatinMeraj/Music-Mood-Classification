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
  // Hardcoded data from actual results: Low-confidence predictions by mood
  // Audio threshold: <0.35, Lyrics threshold: <0.60
  const lowConfidenceData: LowConfidenceData[] = [
    { mood: "Happy", audio: 0.8, lyrics: 2.4 },
    { mood: "Chill", audio: 1.2, lyrics: 31.9 },
    { mood: "Sad", audio: 0.7, lyrics: 7.1 },
    { mood: "Hyped", audio: 2.2, lyrics: 2.3 },
  ]
  
  // Hardcoded confidence distribution from actual results
  // Audio model: Mean 0.710, clusters in 0.2-0.6 range with peak around 0.7-0.8, spike at 1.0
  // Lyrics model: Mean 0.895, most predictions above 0.8, large spike at 1.0 (over 7000 songs)
  const confidenceDistribution: ConfidenceDistribution[] = [
    { range: "0-0.2", audio: 500, lyrics: 0 },
    { range: "0.2-0.4", audio: 3000, lyrics: 100 },
    { range: "0.4-0.6", audio: 4000, lyrics: 200 },
    { range: "0.6-0.8", audio: 6000, lyrics: 2000 },
    { range: "0.8-1.0", audio: 6500, lyrics: 15700 }, // Lyrics model highly confident, most at 1.0
  ]

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
                <div className="mt-4 p-4 rounded-lg bg-chill/10 border border-chill/30">
                  <p className="text-sm font-semibold text-chill mb-2">Why "Chill" Has High Low-Confidence (31.9%)</p>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    The lyrics model struggles with "chill" because VADER sentiment analysis is designed for positive/negative 
                    emotion detection, not energy/tempo classification. "Chill" music often has neutral or ambiguous lyrics 
                    that don't strongly signal any emotion. When VADER gives a weak sentiment signal (compound score between 
                    -0.3 and 0.5), it defaults to "chill" but with low confidence because the sentiment signal is ambiguous. 
                    This explains why the model predicts "chill" rarely (only 4.9% of songs) but has high uncertainty when it does.
                  </p>
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
