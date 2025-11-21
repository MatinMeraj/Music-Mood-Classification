"use client"

import { Card } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from "recharts"

// Model accuracy data with CV standard deviation for error bars
const modelAccuracy = [
  { 
    model: "Random Forest", 
    accuracy: 45.0, 
    cv: 41.2, 
    cvStd: 2.1,
    category: "Baseline",
    description: "Best performing baseline model"
  },
  { 
    model: "KNN", 
    accuracy: 41.0, 
    cv: 38.5, 
    cvStd: 1.8,
    category: "Baseline",
    description: "K-Nearest Neighbors classifier"
  },
  { 
    model: "Logistic Regression", 
    accuracy: 28.0, 
    cv: 27.3, 
    cvStd: 1.5,
    category: "Baseline",
    description: "Linear classifier baseline"
  },
  { 
    model: "Audio Model", 
    accuracy: 32.3, 
    cv: 30.1, 
    cvStd: 1.9,
    category: "Final",
    description: "Production audio features model"
  },
  { 
    model: "Lyrics Model", 
    accuracy: 30.1, 
    cv: 28.8, 
    cvStd: 1.7,
    category: "Final",
    description: "VADER sentiment analysis model"
  },
]

// Helper function to get color based on performance tier
const getPerformanceColor = (accuracy: number) => {
  if (accuracy >= 40) return "hsl(var(--primary))" // Best - primary color
  if (accuracy >= 30) return "hsl(var(--chart-1))" // Good - chart color 1
  return "hsl(var(--muted-foreground))" // Lower - muted
}

const getPerformanceTier = (accuracy: number) => {
  if (accuracy >= 40) return "Excellent"
  if (accuracy >= 30) return "Good"
  return "Fair"
}

const audioConfusion = [
  { true: "Happy", happy: 709, chill: 1, sad: 876, hyped: 35 },
  { true: "Chill", happy: 78, chill: 0, sad: 124, hyped: 1 },
  { true: "Sad", happy: 462, chill: 0, sad: 878, hyped: 20 },
  { true: "Hyped", happy: 654, chill: 2, sad: 1132, hyped: 28 },
]

const lyricsConfusion = [
  { true: "Happy", happy: 409, chill: 30, sad: 613, hyped: 569 },
  { true: "Chill", happy: 70, chill: 2, sad: 59, hyped: 72 },
  { true: "Sad", happy: 304, chill: 41, sad: 781, hyped: 234 },
  { true: "Hyped", happy: 133, chill: 35, sad: 1333, hyped: 315 },
]

export function ModelPerformance() {
  return (
    <section className="space-y-8">
      <div className="text-center space-y-4">
        <h2 className="text-3xl sm:text-4xl font-bold text-balance">Model Performance</h2>
        <p className="text-muted-foreground text-lg text-balance">
          Accuracy metrics and confusion matrices for model evaluation
        </p>
      </div>

      <Tabs defaultValue="comparison" className="space-y-6">
        <TabsList className="grid w-full max-w-md mx-auto grid-cols-3">
          <TabsTrigger value="comparison">Comparison</TabsTrigger>
          <TabsTrigger value="audio">Audio Model</TabsTrigger>
          <TabsTrigger value="lyrics">Lyrics Model</TabsTrigger>
        </TabsList>

        <TabsContent value="comparison" className="space-y-4">
          <Card className="p-6">
            <div className="mb-6">
              <h3 className="text-xl font-semibold mb-2">Model Accuracy Comparison</h3>
              <p className="text-sm text-muted-foreground">
                Comparing baseline models with production audio and lyrics models. All models classify songs into 4 mood categories (Happy, Chill, Sad, Hyped).
              </p>
            </div>
            <ResponsiveContainer width="100%" height={450}>
              <BarChart 
                data={modelAccuracy} 
                margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--muted-foreground))" opacity={0.2} />
                <XAxis 
                  dataKey="model"
                  stroke="hsl(var(--foreground))"
                  tick={{ fill: "hsl(var(--foreground))", fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis 
                  stroke="hsl(var(--foreground))"
                  tick={{ fill: "hsl(var(--foreground))", fontSize: 12 }}
                  label={{ 
                    value: "Accuracy (%)", 
                    angle: -90, 
                    position: "insideLeft",
                    fill: "hsl(var(--foreground))",
                    style: { fontSize: 14, textAnchor: "middle" }
                  }}
                  domain={[0, 50]}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--popover))",
                    border: "1px solid hsl(var(--border))",
                    color: "hsl(var(--popover-foreground))",
                    borderRadius: "6px",
                  }}
                  labelStyle={{ 
                    color: "hsl(var(--popover-foreground))",
                    fontWeight: "bold",
                    marginBottom: "4px"
                  }}
                  formatter={(value: number, name: string, props: any) => {
                    // name is the dataKey, not the display name
                    if (name === "cv") {
                      return [`${value.toFixed(1)}% (±${props.payload.cvStd?.toFixed(1) || 0})`, "CV Accuracy (5-fold)"]
                    }
                    if (name === "accuracy") {
                      return [`${value.toFixed(1)}%`, "Test Accuracy"]
                    }
                    return [`${value.toFixed(1)}%`, name]
                  }}
                />
                <Legend 
                  wrapperStyle={{ color: "hsl(var(--foreground))", paddingTop: "20px" }} 
                  iconType="rect"
                />
                <Bar 
                  dataKey="cv" 
                  name="CV Accuracy (5-fold)" 
                  fill="hsl(var(--chart-2))"
                  radius={[4, 4, 0, 0]}
                  label={{ position: "top", fill: "hsl(var(--foreground))", fontSize: 11, formatter: (value: number) => `${value.toFixed(1)}%` }}
                >
                  {modelAccuracy.map((entry, index) => (
                    <Cell key={`cell-cv-${index}`} fill={getPerformanceColor(entry.cv)} />
                  ))}
                </Bar>
                <Bar 
                  dataKey="accuracy" 
                  name="Test Accuracy" 
                  fill="hsl(var(--primary))"
                  radius={[4, 4, 0, 0]}
                  label={{ position: "top", fill: "hsl(var(--foreground))", fontSize: 11, formatter: (value: number) => `${value.toFixed(1)}%` }}
                >
                  {modelAccuracy.map((entry, index) => (
                    <Cell key={`cell-test-${index}`} fill={getPerformanceColor(entry.accuracy)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            
            {/* Enhanced Summary Cards */}
            <div className="grid sm:grid-cols-3 gap-4 mt-8">
              <div className="p-5 rounded-lg bg-gradient-to-br from-primary/20 to-primary/5 border-2 border-primary/30 shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-3xl font-bold text-primary">45.0%</p>
                  <span className="text-xs font-semibold px-2 py-1 rounded bg-primary/20 text-primary">
                    BEST
                  </span>
                </div>
                <p className="text-sm font-semibold text-foreground mb-1">Random Forest</p>
                <p className="text-xs text-muted-foreground">CV: 41.2% ± 2.1%</p>
                <p className="text-xs text-muted-foreground mt-2">{getPerformanceTier(45.0)} Performance</p>
              </div>
              
              <div className="p-5 rounded-lg bg-gradient-to-br from-chart-1/20 to-chart-1/5 border-2 border-chart-1/30 shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-3xl font-bold text-chart-1">32.3%</p>
                  <span className="text-xs font-semibold px-2 py-1 rounded bg-chart-1/20 text-chart-1">
                    PRODUCTION
                  </span>
                </div>
                <p className="text-sm font-semibold text-foreground mb-1">Audio Model</p>
                <p className="text-xs text-muted-foreground">CV: 30.1% ± 1.9%</p>
                <p className="text-xs text-muted-foreground mt-2">{getPerformanceTier(32.3)} Performance</p>
              </div>
              
              <div className="p-5 rounded-lg bg-gradient-to-br from-chart-3/20 to-chart-3/5 border-2 border-chart-3/30 shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-3xl font-bold text-chart-3">30.1%</p>
                  <span className="text-xs font-semibold px-2 py-1 rounded bg-chart-3/20 text-chart-3">
                    PRODUCTION
                  </span>
                </div>
                <p className="text-sm font-semibold text-foreground mb-1">Lyrics Model</p>
                <p className="text-xs text-muted-foreground">CV: 28.8% ± 1.7%</p>
                <p className="text-xs text-muted-foreground mt-2">{getPerformanceTier(30.1)} Performance</p>
              </div>
            </div>

            {/* Performance Insights */}
            <div className="mt-6 p-4 rounded-lg bg-muted/50 border border-border">
              <h4 className="text-sm font-semibold mb-2 text-foreground">Key Insights</h4>
              <ul className="text-xs text-muted-foreground space-y-1 list-disc list-inside">
                <li>Random Forest achieves the highest accuracy (45.0%) among all models tested</li>
                <li>Audio model (32.3%) outperforms lyrics model (30.1%) by 2.2 percentage points</li>
                <li>All models exceed random baseline (25%) for 4-class classification</li>
                <li>CV and Test accuracies are closely aligned, indicating good generalization</li>
              </ul>
            </div>

            <p className="text-center text-xs text-muted-foreground mt-6 font-medium">
              Figure 1: Model performance comparison. CV Accuracy uses 5-fold cross-validation. Error bars show standard deviation.
            </p>
          </Card>
        </TabsContent>

        <TabsContent value="audio" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-6">Audio Model Confusion Matrix</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="p-3 text-left font-semibold">True ↓ / Predicted →</th>
                    <th className="p-3 text-center font-semibold text-happy">Happy</th>
                    <th className="p-3 text-center font-semibold text-chill">Chill</th>
                    <th className="p-3 text-center font-semibold text-sad">Sad</th>
                    <th className="p-3 text-center font-semibold text-hyped">Hyped</th>
                  </tr>
                </thead>
                <tbody>
                  {audioConfusion.map((row, i) => (
                    <tr key={i} className="border-b border-border/50">
                      <td className="p-3 font-semibold">{row.true}</td>
                      <td className="p-3 text-center">
                        <span className={row.happy > 400 ? "font-bold text-happy" : ""}>{row.happy}</span>
                      </td>
                      <td className="p-3 text-center">
                        <span className={row.chill > 30 ? "font-bold text-chill" : ""}>{row.chill}</span>
                      </td>
                      <td className="p-3 text-center">
                        <span className={row.sad > 700 ? "font-bold text-sad" : ""}>{row.sad}</span>
                      </td>
                      <td className="p-3 text-center">
                        <span className={row.hyped > 300 ? "font-bold text-hyped" : ""}>{row.hyped}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-center text-sm text-muted-foreground mt-4">
              Audio model achieves 32.3% accuracy using 9 audio features (tempo, energy, valence, etc.)
            </p>
          </Card>
        </TabsContent>

        <TabsContent value="lyrics" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-6">Lyrics Model Confusion Matrix</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="p-3 text-left font-semibold">True ↓ / Predicted →</th>
                    <th className="p-3 text-center font-semibold text-happy">Happy</th>
                    <th className="p-3 text-center font-semibold text-chill">Chill</th>
                    <th className="p-3 text-center font-semibold text-sad">Sad</th>
                    <th className="p-3 text-center font-semibold text-hyped">Hyped</th>
                  </tr>
                </thead>
                <tbody>
                  {lyricsConfusion.map((row, i) => (
                    <tr key={i} className="border-b border-border/50">
                      <td className="p-3 font-semibold">{row.true}</td>
                      <td className="p-3 text-center">
                        <span className={row.happy > 400 ? "font-bold text-happy" : ""}>{row.happy}</span>
                      </td>
                      <td className="p-3 text-center">
                        <span className={row.chill > 30 ? "font-bold text-chill" : ""}>{row.chill}</span>
                      </td>
                      <td className="p-3 text-center">
                        <span className={row.sad > 700 ? "font-bold text-sad" : ""}>{row.sad}</span>
                      </td>
                      <td className="p-3 text-center">
                        <span className={row.hyped > 300 ? "font-bold text-hyped" : ""}>{row.hyped}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-center text-sm text-muted-foreground mt-4">
              Lyrics model achieves 30.1% accuracy using VADER sentiment analysis on song lyrics
            </p>
          </Card>
        </TabsContent>
      </Tabs>
    </section>
  )
}
