import { Music } from "lucide-react"

export function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-border bg-gradient-to-br from-background via-primary/5 to-chart-2/10">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-chart-1/20 via-transparent to-chart-4/20 pointer-events-none" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32 relative">
        <div className="text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/15 border-2 border-primary/30 text-sm font-medium text-primary shadow-lg shadow-primary/10">
            <Music className="w-4 h-4" />
            <span>CMPT 310 Project - Group 20</span>
          </div>

          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-balance">
            Spotify Song{" "}
            <span className="bg-gradient-to-r from-chart-1 via-chart-4 to-chart-2 bg-clip-text text-transparent">
              Mood Classifier
            </span>
          </h1>

          <p className="text-xl text-foreground/80 max-w-3xl mx-auto text-balance leading-relaxed">
            A machine learning system that classifies songs into four mood categories using audio features as the main
            method, with lyrics sentiment analysis as a baseline comparison
          </p>

          <div className="flex flex-wrap justify-center gap-4 pt-4">
            <div className="px-6 py-3 rounded-lg bg-card border-2 border-border shadow-lg hover:shadow-xl hover:border-primary/30 transition-all">
              <div className="text-2xl font-bold text-foreground">4</div>
              <div className="text-sm text-muted-foreground">Mood Categories</div>
            </div>
            <div className="px-6 py-3 rounded-lg bg-card border-2 border-border shadow-lg hover:shadow-xl hover:border-primary/30 transition-all">
              <div className="text-2xl font-bold text-foreground">Main Method</div>
              <div className="text-sm text-muted-foreground">Audio Classifier</div>
            </div>
            <div className="px-6 py-3 rounded-lg bg-card border-2 border-border shadow-lg hover:shadow-xl hover:border-primary/30 transition-all">
              <div className="text-2xl font-bold text-foreground">Baseline</div>
              <div className="text-sm text-muted-foreground">Lyrics Classifier</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
