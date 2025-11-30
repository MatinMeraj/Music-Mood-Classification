import { Card } from "@/components/ui/card"
import { AlertTriangle, TrendingUp, Target, GitCompare } from "lucide-react"

const insights = [
  {
    icon: AlertTriangle,
    title: "Low Model Agreement",
    description:
      "Only 25.7% agreement between audio and lyrics models, reflecting how differently audio production and lyrical content express emotion",
    color: "text-primary",
  },
  {
    icon: TrendingUp,
    title: "Audio Model Outperforms",
    description:
      "Audio-based Random Forest model achieves 35.2% accuracy vs. 26% for lyrics model, showing audio features better capture mood",
    color: "text-chart-1",
  },
  {
    icon: Target,
    title: "Largest Mismatch: Hyped vs Sad",
    description: "2,789 songs where audio predicts hyped but lyrics predicts sad, showing energetic production often masks negative lyrics",
    color: "text-hyped",
  },
  {
    icon: GitCompare,
    title: "Complementary Model Strengths",
    description:
      "74.3% disagreement shows models capture different aspects - audio captures emotional tone (tempo, rhythm, intensity), lyrics capture emotional meaning (content, narrative)",
    color: "text-chart-2",
  },
]

export function KeyInsights() {
  return (
    <section className="space-y-8">
      <div className="text-center space-y-4">
        <h2 className="text-3xl sm:text-4xl font-bold text-balance">Key Findings</h2>
        <p className="text-muted-foreground text-lg text-balance">Critical insights from our dual-model analysis</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {insights.map((insight, index) => (
          <Card
            key={index}
            className="p-6 space-y-4 hover:border-primary/50 hover:shadow-xl transition-all border-2 shadow-md"
          >
            <div className={`inline-flex p-3 rounded-lg bg-muted/60 shadow-sm ${insight.color}`}>
              <insight.icon className="w-6 h-6" />
            </div>
            <h3 className="font-semibold text-lg leading-tight text-balance">{insight.title}</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">{insight.description}</p>
          </Card>
        ))}
      </div>
    </section>
  )
}
