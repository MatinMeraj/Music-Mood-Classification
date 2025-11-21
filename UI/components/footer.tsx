import { Github, Mail } from "lucide-react"

export function Footer() {
  return (
    <footer className="border-t border-border mt-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="space-y-3">
            <h3 className="font-semibold text-lg">Spotify Mood Classifier</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              A machine learning project for CMPT 310 exploring dual-model mood classification using audio features and
              lyrics sentiment analysis.
            </p>
          </div>

          <div className="space-y-3">
            <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider">Project Info</h3>
            <ul className="space-y-2 text-sm">
              <li className="text-muted-foreground">Course: CMPT 310</li>
              <li className="text-muted-foreground">Group: 20</li>
              <li className="text-muted-foreground">Milestone: 2</li>
            </ul>
          </div>

          <div className="space-y-3">
            <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider">Resources</h3>
            <div className="flex gap-4">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                <Github className="w-5 h-5" />
                <span>GitHub</span>
              </a>
              <a
                href="mailto:project@example.com"
                className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                <Mail className="w-5 h-5" />
                <span>Contact</span>
              </a>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-border text-center text-sm text-muted-foreground">
          <p>© 2025 Group 20. Built for academic purposes.</p>
        </div>
      </div>
    </footer>
  )
}
