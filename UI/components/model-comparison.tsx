"use client"

import { useState, useEffect, useLayoutEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

if (typeof window !== 'undefined') {
  console.log("ModelComparison: Module loaded (CLIENT), API_BASE_URL:", API_BASE_URL)
} else {
  console.log("ModelComparison: Module loaded (SERVER), API_BASE_URL:", API_BASE_URL)
}

// Default fallback data
const defaultAgreementData = [
  { name: "Agree", value: 0, color: "hsl(var(--chart-2))" },
  { name: "Disagree", value: 0, color: "hsl(var(--chart-4))" },
]

const defaultDistributionData = [
  { mood: "Happy", audio: 0, lyrics: 0 },
  { mood: "Chill", audio: 0, lyrics: 0 },
  { mood: "Sad", audio: 0, lyrics: 0 },
  { mood: "Hyped", audio: 0, lyrics: 0 },
]

const defaultConfusionData = [
  { audio: "Happy", happy: 0, chill: 0, sad: 0, hyped: 0 },
  { audio: "Chill", happy: 0, chill: 0, sad: 0, hyped: 0 },
  { audio: "Sad", happy: 0, chill: 0, sad: 0, hyped: 0 },
  { audio: "Hyped", happy: 0, chill: 0, sad: 0, hyped: 0 },
]

export function ModelComparison() {
  // State declarations must come before any useEffect hooks (React rules)
  const [agreementData, setAgreementData] = useState(defaultAgreementData)
  const [distributionData, setDistributionData] = useState(defaultDistributionData)
  const [confusionData, setConfusionData] = useState(defaultConfusionData)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Test if component is executing at all - use useEffect to ensure it runs on client
  useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).testModelComparison = true
      console.log("ModelComparison: Component mounted on CLIENT")
      
      // Also check for data in body attribute as fallback
      const statsAttr = document.body.getAttribute('data-api-stats')
      if (statsAttr) {
        try {
          const data = JSON.parse(statsAttr)
          console.log("ModelComparison: Found stats in data attribute, updating...")
          
          // Check if data contains an error
          if (!data || data.error) {
            const errorMsg = data?.error || "Failed to load statistics";
            setError(errorMsg);
            setLoading(false);
            return;
          }
          
          // Validate data structure before processing
          if (!data.agreement || !data.distribution || !data.confusion) {
            console.warn("ModelComparison: Incomplete data structure in attribute", data);
            setError("Incomplete data received from API");
            setLoading(false);
            return;
          }
          
          // Update state directly (validation ensures these exist)
          setAgreementData([
            { name: "Agree", value: data.agreement.agree || 0, color: "hsl(var(--chart-2))" },
            { name: "Disagree", value: data.agreement.disagree || 0, color: "hsl(var(--chart-4))" },
          ])
          
          setDistributionData(data.distribution || defaultDistributionData)
          
          const confusion = data.confusion.map((row: any) => ({
            audio: row.audio,
            happy: row.happy || 0,
            chill: row.chill || 0,
            sad: row.sad || 0,
            hyped: row.hyped || 0,
          }))
          setConfusionData(confusion)
          setError(null)
          setLoading(false)
        } catch (e) {
          console.error("Error parsing stats from attribute:", e)
          setError("Failed to parse data from attribute")
          setLoading(false)
        }
      }
    }
  }, [])

  // Try useLayoutEffect first to ensure it runs
  useLayoutEffect(() => {
    console.log("ModelComparison: useLayoutEffect FIRED!")
  }, [])
  
  // Add render-time check
  if (typeof window !== 'undefined') {
    console.log("ModelComparison: Component render, loading:", loading)
  }
  
  useEffect(() => {
    // Register listener with global API data handler
    const handleData = (type: string, data: any) => {
      if (type === 'stats') {
        console.log("ModelComparison: Received stats data:", data)
        
        // Check if data contains an error
        if (!data || data.error) {
          const errorMsg = data?.error || "Failed to load statistics";
          setError(errorMsg);
          setLoading(false);
          return;
        }
        
        // Validate data structure before processing
        if (!data.agreement || !data.distribution || !data.confusion) {
          console.warn("ModelComparison: Incomplete data structure received", data);
          setError("Incomplete data received from API");
          setLoading(false);
          return;
        }
        
        // Process data (validation ensures these exist)
        setAgreementData([
          { name: "Agree", value: data.agreement.agree || 0, color: "hsl(var(--chart-2))" },
          { name: "Disagree", value: data.agreement.disagree || 0, color: "hsl(var(--chart-4))" },
        ])
        
        setDistributionData(data.distribution || defaultDistributionData)
        
        const confusion = data.confusion.map((row: any) => ({
          audio: row.audio,
          happy: row.happy || 0,
          chill: row.chill || 0,
          sad: row.sad || 0,
          hyped: row.hyped || 0,
        }))
        setConfusionData(confusion)
        
        setError(null)
        setLoading(false)
      }
    }

    // Register listener
    if (typeof window !== 'undefined' && (window as any).__registerAPIListener__) {
      (window as any).__registerAPIListener__(handleData)
      console.log("ModelComparison: Registered API listener")
    }
    
    // Also listen for events
    const handleEvent = (event: any) => {
      handleData('stats', event.detail)
    }
    window.addEventListener('api-stats-loaded', handleEvent as EventListener)
    
    // Also try direct fetch as fallback
    const runFetch = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/stats`, {
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
        
        // Validate data structure
        if (!data.agreement || !data.distribution || !data.confusion) {
          throw new Error("Incomplete data received from API");
        }
        
        setAgreementData([
          { name: "Agree", value: data.agreement.agree || 0, color: "hsl(var(--chart-2))" },
          { name: "Disagree", value: data.agreement.disagree || 0, color: "hsl(var(--chart-4))" },
        ])
        
        setDistributionData(data.distribution || defaultDistributionData)
        
        const confusion = data.confusion?.map((row: any) => ({
          audio: row.audio,
          happy: row.happy || 0,
          chill: row.chill || 0,
          sad: row.sad || 0,
          hyped: row.hyped || 0,
        })) || defaultConfusionData
        setConfusionData(confusion)
        
        setError(null)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Failed to load statistics"
        if (errorMessage.includes("Failed to fetch") || errorMessage.includes("aborted") || errorMessage.includes("NetworkError")) {
          setError(`API server not available. Please start the API server: python src/api_server.py`)
        } else {
          setError(errorMessage)
        }
      } finally {
        setLoading(false)
      }
    }

    // Try fetch after a delay to ensure component is mounted
    const timeoutId = setTimeout(() => {
      console.log("ModelComparison: Attempting direct fetch...")
      runFetch()
    }, 500)
    
    // Poll for global data (in case useEffect runs but events don't)
    const pollInterval = setInterval(() => {
      if (typeof window !== 'undefined' && (window as any).__API_DATA__?.stats) {
        const data = (window as any).__API_DATA__.stats
        // Only process if data is valid (not an error object)
        if (data && !data.error) {
          console.log("ModelComparison: Found data in global store, updating...")
          handleData('stats', data)
          clearInterval(pollInterval)
        }
      }
    }, 500)
    
    // Stop polling after 30 seconds to avoid infinite polling
    const pollTimeout = setTimeout(() => {
      clearInterval(pollInterval)
    }, 30000)

    return () => {
      window.removeEventListener('api-stats-loaded', handleEvent as EventListener)
      clearTimeout(timeoutId)
      clearInterval(pollInterval)
      clearTimeout(pollTimeout)
    }
  }, [])
  
  // Manual test button to verify API works
  const handleManualFetch = async (e?: React.MouseEvent) => {
    e?.preventDefault()
    e?.stopPropagation()
    alert("Button clicked! This proves JavaScript is working.")
    console.log("Manual fetch triggered!")
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE_URL}/api/stats`)
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
      const data = await response.json()
      console.log("Manual fetch success:", data)
      
      setAgreementData([
        { name: "Agree", value: data.agreement.agree, color: "hsl(var(--chart-2))" },
        { name: "Disagree", value: data.agreement.disagree, color: "hsl(var(--chart-4))" },
      ])
      setDistributionData(data.distribution || defaultDistributionData)
      const confusion = data.confusion?.map((row: any) => ({
        audio: row.audio,
        happy: row.happy || 0,
        chill: row.chill || 0,
        sad: row.sad || 0,
        hyped: row.hyped || 0,
      })) || defaultConfusionData
      setConfusionData(confusion)
      setError(null)
    } catch (err) {
      console.error("Manual fetch error:", err)
      setError(err instanceof Error ? err.message : "Failed to load")
    } finally {
      setLoading(false)
    }
  }

  if (loading && !error) {
    return (
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl sm:text-4xl font-bold text-balance">Model Comparison</h2>
          <p className="text-muted-foreground text-lg text-balance">
            Loading statistics...
          </p>
          <div>
            <button 
              onClick={() => {
                alert("Plain HTML button works!")
                handleManualFetch()
              }}
              style={{ padding: '10px', backgroundColor: 'blue', color: 'white', border: 'none', cursor: 'pointer' }}
            >
              Test HTML Button
            </button>
            <Button 
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                alert("React Button works!")
                handleManualFetch(e)
              }}
            >
              Click to Load Data (Test)
            </Button>
          </div>
        </div>
      </section>
    )
  }

  if (error) {
    return (
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl sm:text-4xl font-bold text-balance">Model Comparison</h2>
          <p className="text-destructive text-lg">
            Error: {error}
          </p>
          <p className="text-muted-foreground text-sm">
            Make sure the API server is running on {API_BASE_URL}
          </p>
        </div>
      </section>
    )
  }

  return (
    <section className="space-y-8">
      <div className="text-center space-y-4">
        <h2 className="text-3xl sm:text-4xl font-bold text-balance">Model Comparison</h2>
        <p className="text-muted-foreground text-lg text-balance">
          How audio and lyrics models compare in their predictions
        </p>
      </div>

      <Tabs defaultValue="agreement" className="space-y-6">
        <TabsList className="grid w-full max-w-md mx-auto grid-cols-3">
          <TabsTrigger value="agreement">Agreement</TabsTrigger>
          <TabsTrigger value="distribution">Distribution</TabsTrigger>
          <TabsTrigger value="confusion">Confusion</TabsTrigger>
        </TabsList>

        <TabsContent value="agreement" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-6">Overall Model Agreement</h3>
            {agreementData && agreementData.length > 0 ? (
              <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                  <Pie
                    data={agreementData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}%`}
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {agreementData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-muted-foreground py-8">No agreement data available</div>
            )}
            <p className="text-center text-sm text-muted-foreground mt-4 font-medium">
              Figure 2: Agreement between main method (audio) and baseline (lyrics). {agreementData.length > 1 ? `${agreementData[1]?.value || 0}%` : '0%'} disagreement highlights
              complementary strengths.
            </p>
          </Card>
        </TabsContent>

        <TabsContent value="distribution" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-6">Prediction Distribution by Model</h3>
            {distributionData && distributionData.length > 0 ? (
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={distributionData}>
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
                      value: "Percentage (%)",
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
                  <Legend wrapperStyle={{ color: "hsl(var(--foreground))" }} iconType="rect" />
                  <Bar dataKey="audio" name="Audio Model" fill="hsl(var(--chart-1))" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="lyrics" name="Lyrics Model" fill="hsl(var(--chart-3))" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-muted-foreground py-8">No distribution data available</div>
            )}
            <p className="text-center text-sm text-muted-foreground mt-4 font-medium">
              Figure 3: Prediction distribution comparing main method (audio) vs baseline (lyrics) predictions.
            </p>
          </Card>
        </TabsContent>

        <TabsContent value="confusion" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-6">Audio vs Lyrics Confusion Matrix</h3>
            {confusionData && confusionData.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="p-3 text-left font-semibold">Audio ↓ / Lyrics →</th>
                      <th className="p-3 text-center font-semibold text-happy">Happy</th>
                      <th className="p-3 text-center font-semibold text-chill">Chill</th>
                      <th className="p-3 text-center font-semibold text-sad">Sad</th>
                      <th className="p-3 text-center font-semibold text-hyped">Hyped</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(() => {
                      // Calculate dynamic threshold based on data (use 75th percentile for highlighting)
                      // Calculate once outside the map for efficiency
                      const allValues = confusionData.flatMap(r => [r.happy || 0, r.chill || 0, r.sad || 0, r.hyped || 0])
                      const sortedValues = [...allValues].sort((a, b) => b - a)
                      const threshold = sortedValues[Math.floor(sortedValues.length * 0.25)] || 0
                      
                      return confusionData.map((row, i) => (
                        <tr key={i} className="border-b border-border/50">
                          <td className="p-3 font-semibold">{row.audio || 'Unknown'}</td>
                          <td className="p-3 text-center">
                            <span className={(row.happy || 0) > threshold ? "font-bold text-happy" : ""}>{row.happy || 0}</span>
                          </td>
                          <td className="p-3 text-center">
                            <span className={(row.chill || 0) > threshold ? "font-bold text-chill" : ""}>{row.chill || 0}</span>
                          </td>
                          <td className="p-3 text-center">
                            <span className={(row.sad || 0) > threshold ? "font-bold text-sad" : ""}>{row.sad || 0}</span>
                          </td>
                          <td className="p-3 text-center">
                            <span className={(row.hyped || 0) > threshold ? "font-bold text-hyped" : ""}>{row.hyped || 0}</span>
                          </td>
                        </tr>
                      ))
                    })()}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center text-muted-foreground py-8">No confusion matrix data available</div>
            )}
            <p className="text-center text-sm text-muted-foreground mt-4 font-medium">
              Figure 4: Confusion matrix comparing main method (audio) vs baseline (lyrics) predictions.
            </p>
          </Card>
        </TabsContent>
      </Tabs>
    </section>
  )
}
