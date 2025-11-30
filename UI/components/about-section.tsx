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
            acousticness, instrumentalness, and liveness. Pipeline: Input → Imputation → Standardization → Model Training →
            Model Prediction. Random Forest performed best with 35.2% test accuracy (vs. 25% random chance).
          </p>
        </Card>

        <Card className="p-6 space-y-4">
          <div className="inline-flex p-3 rounded-lg bg-chart-3/10">
            <Brain className="w-6 h-6 text-chart-3" />
          </div>
          <h3 className="text-xl font-semibold">Lyrics Sentiment Model</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Applies VADER (Valence Aware Dictionary and sEntiment Reasoner), a rule-based sentiment analyzer, to song lyrics.
            Sentiment scores (positive, negative, neutral) are mapped to compound scores and then to the four mood classes. The
            lyrics model achieved 26% accuracy with a strong bias toward sad and happy.
          </p>
        </Card>

        <Card className="p-6 space-y-4">
          <div className="inline-flex p-3 rounded-lg bg-primary/10">
            <Database className="w-6 h-6 text-primary" />
          </div>
          <h3 className="text-xl font-semibold">Dataset</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Started with 500,000 tracks containing audio features and mood labels from 10 categories. Mapped to 4 target moods
            (happy, chill, sad, hyped) and downsampled to create a balanced dataset of 20,000 songs (5,000 per mood). Data
            sourced from Spotify with both audio features and lyrics for comprehensive analysis.
          </p>
        </Card>

        <Card className="p-6 space-y-4">
          <div className="inline-flex p-3 rounded-lg bg-chart-2/10">
            <TrendingUp className="w-6 h-6 text-chart-2" />
          </div>
          <h3 className="text-xl font-semibold">Evaluation</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Models evaluated using accuracy, confusion matrices, and confidence thresholds. Among Logistic Regression, KNN,
            and Random Forest, the Random Forest performed best with 35.2% test accuracy (vs. 25% random chance). The lyrics
            model achieved 26% accuracy with a strong bias toward sad and happy. Agreement analysis shows 25.9% agreement
            between the two pipelines.
          </p>
        </Card>
      </div>
    </section>
  )
}
