"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

const defaultDistribution = [
  { mood: "Happy", count: 0, color: "hsl(var(--happy))" },
  { mood: "Chill", count: 0, color: "hsl(var(--chill))" },
  { mood: "Sad", count: 0, color: "hsl(var(--sad))" },
  { mood: "Hyped", count: 0, color: "hsl(var(--hyped))" },
]

export function DatasetExplorer() {
  const [datasetDistribution, setDatasetDistribution] = useState(defaultDistribution)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    if (typeof window !== 'undefined') {
      console.log("DatasetExplorer: Component mounted on CLIENT")
      
      // Check for data in body attribute as fallback
      const datasetAttr = document.body.getAttribute('data-api-dataset')
      if (datasetAttr) {
        try {
          const data = JSON.parse(datasetAttr)
          console.log("DatasetExplorer: Found dataset in data attribute, updating...")
          const moodColors: Record<string, string> = {
            "Happy": "hsl(var(--happy))",
            "Chill": "hsl(var(--chill))",
            "Sad": "hsl(var(--sad))",
            "Hyped": "hsl(var(--hyped))",
          }
          const distribution = data.distribution.map((item: any) => ({
            mood: item.mood,
            count: item.count,
            color: moodColors[item.mood] || "hsl(var(--muted-foreground))",
          }))
          setDatasetDistribution(distribution)
          setTotal(data.total || 0)
          setError(null)
          setLoading(false)
        } catch (e) {
          console.error("Error parsing dataset from attribute:", e)
        }
      }
    }
  }, [])

  useEffect(() => {
    // Register listener with global API data handler
    const handleData = (type: string, data: any) => {
      if (type === 'dataset') {
        console.log("DatasetExplorer: Received dataset data:", data)
        
        // Check if data contains an error
        if (!data || data.error) {
          const errorMsg = data?.error || "Failed to load dataset statistics";
          setError(errorMsg);
          setLoading(false);
          return;
        }
        
        // Validate data structure
        if (!data.distribution || !Array.isArray(data.distribution)) {
          console.warn("DatasetExplorer: Invalid data structure received", data);
          setError("Invalid data structure received from API");
          setLoading(false);
          return;
        }
        
        const moodColors: Record<string, string> = {
          "Happy": "hsl(var(--happy))",
          "Chill": "hsl(var(--chill))",
          "Sad": "hsl(var(--sad))",
          "Hyped": "hsl(var(--hyped))",
        }
        
        // Validate and map distribution data
        const distribution = data.distribution
          .filter((item: any) => item && item.mood && typeof item.count === 'number')
          .map((item: any) => ({
            mood: item.mood,
            count: Math.max(0, item.count), // Ensure non-negative
            color: moodColors[item.mood] || "hsl(var(--muted-foreground))",
          }))
        
        if (distribution.length === 0) {
          setError("No valid distribution data in response");
          setLoading(false);
          return;
        }
        
        setDatasetDistribution(distribution)
        setTotal(Math.max(0, data.total || 0))
        setError(null)
        setLoading(false)
      }
    }

    // Register listener
    if (typeof window !== 'undefined' && (window as any).__registerAPIListener__) {
      (window as any).__registerAPIListener__(handleData)
      console.log("DatasetExplorer: Registered API listener")
    }
    
    // Also listen for events
    const handleEvent = (event: any) => {
      handleData('dataset', event.detail)
    }
    window.addEventListener('api-dataset-loaded', handleEvent as EventListener)
    
    // Also try direct fetch as fallback
    const fetchDatasetStats = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/dataset`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        
        // Check if response contains an error
        if (data && data.error) {
          throw new Error(data.error);
        }
        
        // Validate response structure
        if (!data.distribution || !Array.isArray(data.distribution)) {
          throw new Error("Invalid data structure received from API");
        }
        
        const moodColors: Record<string, string> = {
          "Happy": "hsl(var(--happy))",
          "Chill": "hsl(var(--chill))",
          "Sad": "hsl(var(--sad))",
          "Hyped": "hsl(var(--hyped))",
        }
        
        // Validate and map distribution data
        const distribution = data.distribution
          .filter((item: any) => item && item.mood && typeof item.count === 'number')
          .map((item: any) => ({
            mood: item.mood,
            count: Math.max(0, item.count), // Ensure non-negative
            color: moodColors[item.mood] || "hsl(var(--muted-foreground))",
          }))
        
        if (distribution.length === 0) {
          throw new Error("No valid distribution data in response");
        }
        
        setDatasetDistribution(distribution)
        setTotal(Math.max(0, data.total || 0))
        setError(null)
      } catch (err) {
        console.error("Error fetching dataset stats:", err)
        const errorMessage = err instanceof Error ? err.message : "Failed to load dataset statistics"
        if (errorMessage.includes("Failed to fetch") || errorMessage.includes("aborted")) {
          setError(`API server not available. Please start the API server: python src/api_server.py`)
        } else {
          setError(errorMessage)
        }
        // Use default hardcoded data as fallback
        setDatasetDistribution([
          { mood: "Happy", count: 214602, color: "hsl(var(--happy))" },
          { mood: "Chill", count: 27966, color: "hsl(var(--chill))" },
          { mood: "Sad", count: 171078, color: "hsl(var(--sad))" },
          { mood: "Hyped", count: 137777, color: "hsl(var(--hyped))" },
        ])
        setTotal(551423)
      } finally {
        setLoading(false)
      }
    }

    // Try fetch after a delay
    const timeoutId = setTimeout(() => {
      console.log("DatasetExplorer: Attempting direct fetch...")
      fetchDatasetStats()
    }, 500)
    
    // Poll for global data
    const pollInterval = setInterval(() => {
      if (typeof window !== 'undefined' && (window as any).__API_DATA__?.dataset) {
        const data = (window as any).__API_DATA__.dataset
        // Only process if data is valid (not an error object)
        if (data && !data.error) {
          console.log("DatasetExplorer: Found data in global store, updating...")
          handleData('dataset', data)
          clearInterval(pollInterval)
        }
      }
    }, 500)
    
    // Stop polling after 30 seconds to avoid infinite polling
    const pollTimeout = setTimeout(() => {
      clearInterval(pollInterval)
    }, 30000)

    return () => {
      window.removeEventListener('api-dataset-loaded', handleEvent as EventListener)
      clearTimeout(timeoutId)
      clearInterval(pollInterval)
      clearTimeout(pollTimeout)
    }
  }, [])
  
  if (loading) {
    return (
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl sm:text-4xl font-bold text-balance">Dataset Overview</h2>
          <p className="text-muted-foreground text-lg text-balance">
            Loading dataset statistics...
          </p>
        </div>
      </section>
    )
  }

  const displayTotal = total || 551423

  return (
    <section className="space-y-8">
      <div className="text-center space-y-4">
        <h2 className="text-3xl sm:text-4xl font-bold text-balance">Dataset Overview</h2>
        <p className="text-muted-foreground text-lg text-balance">
          Understanding the distribution and balance of our training data
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30 text-yellow-700 text-sm max-w-2xl mx-auto">
          <p className="font-semibold mb-1">Warning: {error}</p>
          <p className="text-xs">Showing fallback data. Start the API server for live data.</p>
        </div>
      )}

      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-6">Mood Class Distribution</h3>
        {datasetDistribution && datasetDistribution.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={datasetDistribution}>
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
                value: "Song Count",
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
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
              {datasetDistribution.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        ) : (
          <div className="text-center text-muted-foreground py-8">No distribution data available</div>
        )}

        {datasetDistribution && datasetDistribution.length > 0 && (
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
          {datasetDistribution.map((item) => (
            <div key={item.mood} className="p-4 rounded-lg border border-border">
              <p className="text-sm text-muted-foreground mb-1">{item.mood}</p>
              <p className="text-2xl font-bold" style={{ color: item.color }}>
                {(item.count / 1000).toFixed(0)}K
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {displayTotal > 0 ? ((item.count / displayTotal) * 100).toFixed(1) : '0.0'}% of total
              </p>
            </div>
          ))}
          </div>
        )}

        <div className="mt-6 p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
          <h4 className="font-semibold text-sm text-yellow-700 mb-2">Class Imbalance Warning</h4>
          <p className="text-xs text-muted-foreground">
            The dataset shows significant imbalance with &quot;Chill&quot; having only 27,966 samples (5.1%) compared to
            &quot;Happy&quot; with 214,602 (38.9%). This imbalance may affect model performance and explains some
            prediction biases.
          </p>
        </div>
        <p className="text-center text-sm text-muted-foreground mt-4 font-medium">
          Figure 7: Balanced dataset distribution after sampling evenly from each mood class.
        </p>
      </Card>
    </section>
  )
}
