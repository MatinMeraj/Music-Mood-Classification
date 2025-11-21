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

const agreementData = [
  { name: "Agree", value: 42.5, color: "hsl(var(--chart-2))" },
  { name: "Disagree", value: 57.5, color: "hsl(var(--chart-4))" },
]

const distributionData = [
  { mood: "Happy", audio: 38.1, lyrics: 18.3 },
  { mood: "Chill", audio: 0.1, lyrics: 2.2 },
  { mood: "Sad", audio: 60.2, lyrics: 55.7 },
  { mood: "Hyped", audio: 1.7, lyrics: 23.8 },
]

const confusionData = [
  { audio: "Happy", happy: 367, chill: 36, sad: 1023, hyped: 477 },
  { audio: "Chill", happy: 0, chill: 0, sad: 2, hyped: 1 },
  { audio: "Sad", happy: 531, chill: 67, sad: 1728, hyped: 684 },
  { audio: "Hyped", happy: 18, chill: 5, sad: 33, hyped: 28 },
]

export function ModelComparison() {
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
            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <Pie
                  data={agreementData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}%`}
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
              Figure 2: Agreement between main method (audio) and baseline (lyrics). 57.5% disagreement highlights
              complementary strengths.
            </p>
          </Card>
        </TabsContent>

        <TabsContent value="distribution" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-6">Prediction Distribution by Model</h3>
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
                  {confusionData.map((row, i) => (
                    <tr key={i} className="border-b border-border/50">
                      <td className="p-3 font-semibold">{row.audio}</td>
                      <td className="p-3 text-center">
                        <span className={row.happy > 350 ? "font-bold text-happy" : ""}>{row.happy}</span>
                      </td>
                      <td className="p-3 text-center">
                        <span className={row.chill > 30 ? "font-bold text-chill" : ""}>{row.chill}</span>
                      </td>
                      <td className="p-3 text-center">
                        <span className={row.sad > 1500 ? "font-bold text-sad" : ""}>{row.sad}</span>
                      </td>
                      <td className="p-3 text-center">
                        <span className={row.hyped > 400 ? "font-bold text-hyped" : ""}>{row.hyped}</span>
                      </td>
                    </tr>
                  ))}
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
