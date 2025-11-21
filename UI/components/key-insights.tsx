import { Card } from "@/components/ui/card"
import { AlertTriangle, TrendingUp, Target, GitCompare } from "lucide-react"

const insights = [
  {
    icon: AlertTriangle,
    title: 'Audio Model Struggles with "Hyped"',
    description:
      "79.8% of hyped predictions are low-confidence, indicating difficulty distinguishing high-energy moods",
    color: "text-hyped",
  },
  {
    icon: TrendingUp,
    title: "Lyrics Baseline More Confident",
    description:
      "Mean confidence of 0.920 vs 0.403 for audio, though VADER is rule-based and not trained on this dataset",
    color: "text-chart-2",
  },
  {
    icon: Target,
    title: 'Best Agreement on "Sad"',
    description: "57.4% agreement rate for sad songs (1728/3010), where both audio and lyrical cues align strongly",
    color: "text-sad",
  },
  {
    icon: GitCompare,
    title: "Complementary Model Strengths",
    description:
      "57.5% disagreement shows models capture different aspects - audio captures music, lyrics capture sentiment",
    color: "text-primary",
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
