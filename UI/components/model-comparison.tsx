"use client"

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
  // Hardcoded data from actual results: 25.7% agreement, 74.3% disagreement (5,135 agree, 14,865 disagree out of 20,000)
  const agreementData: AgreementData[] = [
    { name: "Agree", value: 25.7, color: "hsl(var(--chart-2))" },
    { name: "Disagree", value: 74.3, color: "hsl(var(--chart-4))" },
]

  // Hardcoded distribution data from actual results (percentages based on 20,000 songs)
  // Audio: Happy 5,597 (28.0%), Chill 5,057 (25.3%), Sad 4,652 (23.3%), Hyped 4,694 (23.5%)
  // Lyrics: Happy 6,049 (30.2%), Chill 972 (4.9%), Sad 7,513 (37.6%), Hyped 5,466 (27.3%)
  const distributionData: DistributionData[] = [
    { mood: "Happy", audio: 28.0, lyrics: 30.2 },
    { mood: "Chill", audio: 25.3, lyrics: 4.9 },
    { mood: "Sad", audio: 23.3, lyrics: 37.6 },
    { mood: "Hyped", audio: 23.5, lyrics: 27.3 },
]

  // Hardcoded confusion matrix from actual results: Audio (rows) vs Lyrics (columns)
  // Largest mismatch: Audio predicts hyped, Lyrics predicts sad (2,789 songs)
  const confusionData: ConfusionData[] = [
    { audio: "Happy", happy: 1859, chill: 272, sad: 1633, hyped: 1833 },
    { audio: "Chill", happy: 2134, chill: 215, sad: 1005, hyped: 1703 },
    { audio: "Sad", happy: 1316, chill: 295, sad: 2086, hyped: 955 },
    { audio: "Hyped", happy: 740, chill: 190, sad: 2789, hyped: 975 }, // 2,789 mismatch highlighted
  ]

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
                          <span className={
                            (Number(row.sad) || 0) > threshold || (row.audio === "Hyped" && Number(row.sad) === 2789)
                              ? "font-bold text-sad underline" 
                              : ""
                          }>
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
              Figure 4: Confusion matrix comparing audio vs lyrics predictions. The largest mismatch occurs when audio predicts hyped but lyrics predicts sad (2,789 songs highlighted in bold), showing that energetic production often masks emotionally negative lyrics. This low overlap reflects how differently mood is expressed by audio (emotional tone: tempo, rhythm, intensity) and lyrics (emotional meaning: content, narrative).
            </p>
          </Card>
        </TabsContent>
      </Tabs>
    </section>
  )
}
