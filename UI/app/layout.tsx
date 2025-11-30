import type React from "react"
import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"

const _geist = Geist({ subsets: ["latin"] })
const _geistMono = Geist_Mono({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Spotify Mood Classifier - ML Project",
  description:
    "Machine learning system that classifies songs into mood categories using audio features and lyrics sentiment analysis",
  generator: "v0.app",
  icons: {
    icon: [
      {
        url: "/icon-light-32x32.png",
        media: "(prefers-color-scheme: light)",
      },
      {
        url: "/icon-dark-32x32.png",
        media: "(prefers-color-scheme: dark)",
      },
      {
        url: "/icon.svg",
        type: "image/svg+xml",
      },
    ],
    apple: "/apple-icon.png",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              console.log("Inline script executed - JavaScript is working!");
              window.__TEST_SCRIPT_LOADED__ = true;
              
              // Store API data globally so React components can access it
              window.__API_DATA__ = {
                stats: null,
                dataset: null,
                listeners: []
              };
              
              // Function to notify all listeners
              function notifyListeners(type, data) {
                window.__API_DATA__[type] = data;
                window.__API_DATA__.listeners.forEach(listener => {
                  try {
                    listener(type, data);
                  } catch (e) {
                    console.error("Error in listener:", e);
                  }
                });
                // Also dispatch event
                window.dispatchEvent(new CustomEvent('api-' + type + '-loaded', { detail: data }));
              }
              
              // Wait for page to load, then trigger API calls manually
              window.addEventListener('DOMContentLoaded', function() {
                console.log("DOM loaded, attempting to trigger API calls...");
                
                // Function to trigger API calls
                function triggerAPICalls() {
                  const API_BASE = 'http://localhost:8000';
                  
                  // Trigger stats API call
                  fetch(API_BASE + '/api/stats')
                    .then(res => {
                      if (!res.ok) {
                        throw new Error('HTTP error! status: ' + res.status);
                      }
                      return res.json();
                    })
                    .then(data => {
                      // Check if response contains an error
                      if (data && data.error) {
                        console.error("API stats error:", data.error);
                        return; // Don't notify listeners with error data
                      }
                      console.log("API stats response:", data);
                      notifyListeners('stats', data);
                    })
                    .catch(err => {
                      console.error("API stats error:", err);
                      // Don't notify listeners on error - they'll handle it via polling/direct fetch
                    });
                  
                  // Trigger dataset API call
                  fetch(API_BASE + '/api/dataset')
                    .then(res => {
                      if (!res.ok) {
                        throw new Error('HTTP error! status: ' + res.status);
                      }
                      return res.json();
                    })
                    .then(data => {
                      // Check if response contains an error
                      if (data && data.error) {
                        console.error("API dataset error:", data.error);
                        return; // Don't notify listeners with error data
                      }
                      console.log("API dataset response:", data);
                      notifyListeners('dataset', data);
                    })
                    .catch(err => {
                      console.error("API dataset error:", err);
                      // Don't notify listeners on error - they'll handle it via polling/direct fetch
                    });
                }
                
                // Try immediately and also after delays
                triggerAPICalls();
                setTimeout(triggerAPICalls, 1000);
                setTimeout(triggerAPICalls, 3000);
                
                // Also try when window loads
                window.addEventListener('load', triggerAPICalls);
                
                // After a longer delay, try to notify any registered listeners again
                setTimeout(() => {
                  console.log("Checking for registered listeners and notifying...");
                  console.log("Total listeners registered:", window.__API_DATA__.listeners.length);
                  console.log("React loaded?", typeof window !== 'undefined' && (window as any).React !== undefined);
                  console.log("Test flags:", {
                    testModelComparison: (window as any).testModelComparison,
                    testPredictionInterface: (window as any).testPredictionInterface
                  });
                  
                  if (window.__API_DATA__.stats) {
                    console.log("Notifying listeners with stats data");
                    window.__API_DATA__.listeners.forEach((listener, index) => {
                      try {
                        console.log("Calling listener", index);
                        listener('stats', window.__API_DATA__.stats);
                      } catch (e) {
                        console.error("Error notifying listener:", e);
                      }
                    });
                    // Also dispatch event again
                    window.dispatchEvent(new CustomEvent('api-stats-loaded', { detail: window.__API_DATA__.stats }));
                  }
                  if (window.__API_DATA__.dataset) {
                    console.log("Notifying listeners with dataset data");
                    window.__API_DATA__.listeners.forEach((listener, index) => {
                      try {
                        console.log("Calling listener", index);
                        listener('dataset', window.__API_DATA__.dataset);
                      } catch (e) {
                        console.error("Error notifying listener:", e);
                      }
                    });
                    window.dispatchEvent(new CustomEvent('api-dataset-loaded', { detail: window.__API_DATA__.dataset }));
                  }
                  
                  // Also try to directly update via data attributes as fallback
                  if (window.__API_DATA__.stats) {
                    const statsStr = JSON.stringify(window.__API_DATA__.stats);
                    document.body.setAttribute('data-api-stats', statsStr);
                    console.log("Set data-api-stats attribute on body");
                  }
                  if (window.__API_DATA__.dataset) {
                    const datasetStr = JSON.stringify(window.__API_DATA__.dataset);
                    document.body.setAttribute('data-api-dataset', datasetStr);
                    console.log("Set data-api-dataset attribute on body");
                  }
                }, 5000);
              });
              
              // Expose function for React components to register listeners
              window.__registerAPIListener__ = function(listener) {
                console.log("Registering new API listener, total listeners:", window.__API_DATA__.listeners.length + 1);
                window.__API_DATA__.listeners.push(listener);
                // If data already loaded, notify immediately
                if (window.__API_DATA__.stats) {
                  console.log("Immediately notifying new listener with stats");
                  listener('stats', window.__API_DATA__.stats);
                }
                if (window.__API_DATA__.dataset) {
                  console.log("Immediately notifying new listener with dataset");
                  listener('dataset', window.__API_DATA__.dataset);
                }
              };
            `,
          }}
        />
      </head>
      <body className={`font-sans antialiased`}>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
