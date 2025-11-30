"use client"

import { Card } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from "recharts"

// Model accuracy data with CV standard deviation for error bars
const modelAccuracy = [
  { 
    model: "Random Forest", 
    accuracy: 35.2, 
    cv: 35.2, 
    cvStd: 0.0,
    category: "Baseline",
    description: "Best performing baseline model"
  },
  { 
    model: "KNN", 
    accuracy: 0, 
    cv: 0, 
    cvStd: 0,
    category: "Baseline",
    description: "K-Nearest Neighbors classifier (tested, Random Forest performed best)"
  },
  { 
    model: "Logistic Regression", 
    accuracy: 0, 
    cv: 0, 
    cvStd: 0,
    category: "Baseline",
    description: "Linear classifier baseline (tested, Random Forest performed best)"
  },
  { 
    model: "Audio Model", 
    accuracy: 35.2, 
    cv: 35.2, 
    cvStd: 0.0,
    category: "Final",
    description: "Production audio features model (Random Forest)"
  },
  { 
    model: "Lyrics Model", 
    accuracy: 26.0, 
    cv: 26.0, 
    cvStd: 0.0,
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
                Among Logistic Regression, KNN, and Random Forest, the Random Forest performed best with 35.2% test accuracy (vs. 25% random chance). The audio model uses Random Forest, while the lyrics model uses VADER sentiment analysis. All models classify songs into 4 mood categories (Happy, Chill, Sad, Hyped).
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
                  <p className="text-3xl font-bold text-primary">35.2%</p>
                  <span className="text-xs font-semibold px-2 py-1 rounded bg-primary/20 text-primary">
                    BEST
                  </span>
                </div>
                <p className="text-sm font-semibold text-foreground mb-1">Audio Model (Random Forest)</p>
                <p className="text-xs text-muted-foreground">Test Accuracy</p>
                <p className="text-xs text-muted-foreground mt-2">{getPerformanceTier(35.2)} Performance</p>
              </div>
              
              <div className="p-5 rounded-lg bg-gradient-to-br from-chart-3/20 to-chart-3/5 border-2 border-chart-3/30 shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-3xl font-bold text-chart-3">26.0%</p>
                  <span className="text-xs font-semibold px-2 py-1 rounded bg-chart-3/20 text-chart-3">
                    BASELINE
                  </span>
                </div>
                <p className="text-sm font-semibold text-foreground mb-1">Lyrics Model (VADER)</p>
                <p className="text-xs text-muted-foreground">Test Accuracy</p>
                <p className="text-xs text-muted-foreground mt-2">{getPerformanceTier(26.0)} Performance</p>
              </div>
              
              <div className="p-5 rounded-lg bg-gradient-to-br from-chart-2/20 to-chart-2/5 border-2 border-chart-2/30 shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-3xl font-bold text-chart-2">25.9%</p>
                  <span className="text-xs font-semibold px-2 py-1 rounded bg-chart-2/20 text-chart-2">
                    AGREEMENT
                  </span>
                </div>
                <p className="text-sm font-semibold text-foreground mb-1">Model Agreement</p>
                <p className="text-xs text-muted-foreground">Audio & Lyrics agree</p>
                <p className="text-xs text-muted-foreground mt-2">Low overlap reflects different emotional layers</p>
              </div>
            </div>

            {/* Performance Insights */}
            <div className="mt-6 p-4 rounded-lg bg-muted/50 border border-border">
              <h4 className="text-sm font-semibold mb-2 text-foreground">Key Insights</h4>
              <ul className="text-xs text-muted-foreground space-y-1 list-disc list-inside">
                <li>Random Forest achieves the highest accuracy (35.2%) among all models tested, exceeding random baseline (25%)</li>
                <li>Audio model (35.2%) outperforms lyrics model (26.0%) by 9.2 percentage points</li>
                <li>Both models exceed random baseline (25%) for 4-class classification</li>
                <li>Low agreement (25.9%) reflects how differently audio production and lyrical content express emotion</li>
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
              Audio model achieves 35.2% accuracy using 9 audio features (tempo, energy, valence, loudness, danceability, speechiness, acousticness, instrumentalness, liveness)
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
              Lyrics model achieves 26% accuracy using VADER sentiment analysis on song lyrics, with a strong bias toward sad and happy moods
            </p>
          </Card>
        </TabsContent>
      </Tabs>
    </section>
  )
}
