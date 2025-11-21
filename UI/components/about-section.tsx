import { Card } from "@/components/ui/card"
import { Database, Music2, Brain, TrendingUp } from "lucide-react"

export function AboutSection() {
  return (
    <section className="space-y-8">
      <div className="text-center space-y-4">
        <h2 className="text-3xl sm:text-4xl font-bold text-balance">Methodology</h2>
        <p className="text-muted-foreground text-lg text-balance">
          How we built and evaluated our dual-model classification system
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card className="p-6 space-y-4">
          <div className="inline-flex p-3 rounded-lg bg-chart-1/10">
            <Music2 className="w-6 h-6 text-chart-1" />
          </div>
          <h3 className="text-xl font-semibold">Audio Feature Model</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Extracts 9 audio features from Spotify API: tempo, energy, valence, loudness, danceability, speechiness,
            acousticness, instrumentalness, and liveness. Uses Random Forest classifier with hyperparameter tuning for
            optimal performance.
          </p>
        </Card>

        <Card className="p-6 space-y-4">
          <div className="inline-flex p-3 rounded-lg bg-chart-3/10">
            <Brain className="w-6 h-6 text-chart-3" />
          </div>
          <h3 className="text-xl font-semibold">Lyrics Sentiment Model</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Applies VADER (Valence Aware Dictionary and sEntiment Reasoner) sentiment analysis to song lyrics.
            Classifies moods based on compound sentiment scores, capturing emotional content from textual data.
          </p>
        </Card>

        <Card className="p-6 space-y-4">
          <div className="inline-flex p-3 rounded-lg bg-primary/10">
            <Database className="w-6 h-6 text-primary" />
          </div>
          <h3 className="text-xl font-semibold">Dataset</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            551,423 songs across 4 mood categories (Happy: 214K, Chill: 28K, Sad: 171K, Hyped: 138K). Data sourced from
            Spotify with both audio features and lyrics for comprehensive analysis. Class imbalance addressed through
            weighted loss functions and balanced sampling.
          </p>
        </Card>

        <Card className="p-6 space-y-4">
          <div className="inline-flex p-3 rounded-lg bg-chart-2/10">
            <TrendingUp className="w-6 h-6 text-chart-2" />
          </div>
          <h3 className="text-xl font-semibold">Evaluation</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Models evaluated using accuracy, confusion matrices, and confidence thresholds. Cross-validation performed
            with multiple classifiers (Random Forest: 45%, KNN: 41%, LogReg: 28%). Agreement analysis reveals
            complementary strengths between audio and lyrics approaches.
          </p>
        </Card>
      </div>
    </section>
  )
}
