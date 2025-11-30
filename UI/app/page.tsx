"use client"

import { useState, useEffect } from "react"
import { Hero } from "@/components/hero"
import { PredictionInterface } from "@/components/prediction-interface"
import { ModelComparison } from "@/components/model-comparison"
import { UncertaintyAnalysis } from "@/components/uncertainty-analysis"
import { ModelPerformance } from "@/components/model-performance"
import { DatasetExplorer } from "@/components/dataset-explorer"
import { KeyInsights } from "@/components/key-insights"
import { AboutSection } from "@/components/about-section"
import { Footer } from "@/components/footer"

export default function Home() {
  return (
    <main className="min-h-screen">
      <Hero />
      <PredictionInterface />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-24">
        <KeyInsights />
        <ModelComparison />
        <UncertaintyAnalysis />
        <ModelPerformance />
        <DatasetExplorer />
        <AboutSection />
      </div>
      <Footer />
    </main>
  )
}
