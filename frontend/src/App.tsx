import { useState, useEffect } from 'react'
import axios from 'axios'
import toast, { Toaster } from 'react-hot-toast'
import { motion, AnimatePresence } from 'framer-motion'
import './App.css'

import { UploadSection, AgentProgress, DesignPlan, ResultsSection } from './components'

// Determine API URL based on environment
// For production, set VITE_API_URL in your deployment environment
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Type definitions
interface AgentStatus {
  status: string
  current_step: string
  steps_completed: string[]
  progress_percentage: number
  messages: Array<{
    timestamp: string
    message: string
  }>
  errors: string[]
}

interface DesignPlanResponse {
  plan: string
  status: string
}

interface FurnitureItem {
  title: string
  price: string | null
  google_link: string | null
  direct_link: string | null
  source: string | null
  delivery: string | null
  product_rating: number | null
  product_reviews: number | null
  store_rating: number | null
  store_reviews: number | null
  category: string | null
  position: { x: number; y: number } | null
  image_url: string | null
  local_image_path: string | null
}

interface FinalResults {
  session_id: string
  original_image: string
  designed_image: string
  design_plan: any
  total_cost_estimate: number
  furniture_items: FurnitureItem[]
  completion_time: number
  design_description: string
}

function App() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null)
  const [designPlan, setDesignPlan] = useState<string>('')
  const [finalResults, setFinalResults] = useState<FinalResults | null>(null)
  const [isPolling, setIsPolling] = useState<boolean>(false)

  // Poll for agent status
  useEffect(() => {
    if (sessionId && isPolling) {
      const interval = setInterval(async () => {
        try {
          const statusRes = await axios.get<AgentStatus>(`${API_URL}/api/agent/status/${sessionId}`)
          setAgentStatus(statusRes.data)

          // Get design plan
          const planRes = await axios.get<DesignPlanResponse>(`${API_URL}/api/agent/plan/${sessionId}`)
          setDesignPlan(planRes.data.plan)

          // Check if completed
          if (statusRes.data.status === 'completed') {
            const resultsRes = await axios.get<FinalResults>(`${API_URL}/api/agent/results/${sessionId}`)
            setFinalResults(resultsRes.data)
            setIsPolling(false)
            toast.success('Design completed!')
          } else if (statusRes.data.status === 'error') {
            setIsPolling(false)
            toast.error('Agent encountered an error')
          }
        } catch (error: any) {
          console.error('Polling error:', error)
          // If agent not found, clear session and stop polling
          if (error.response?.status === 404 || error.response?.data?.detail?.includes('not found')) {
            localStorage.removeItem('designSessionId')
            setSessionId(null)
            setIsPolling(false)
            toast.error('Session expired. Please upload a new image.')
          }
        }
      }, 2000) // Poll every 2 seconds

      return () => clearInterval(interval)
    }
  }, [sessionId, isPolling])

  const handleUpload = async (file: File) => {
    try {
      const formData = new FormData()
      formData.append('file', file)

      // Upload file
      const uploadRes = await axios.post<{ success: boolean; session_id: string; file_path: string; filename: string }>(
        `${API_URL}/api/upload`, 
        formData, 
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      )

      const newSessionId = uploadRes.data.session_id
      setSessionId(newSessionId)

      // Start agent
      await axios.post(`${API_URL}/api/agent/start/${newSessionId}`)
      setIsPolling(true)
      toast.success('Agent started! Analyzing your room...')
    } catch (error) {
      console.error('Upload error:', error)
      toast.error('Failed to upload image')
    }
  }

  const resetAgent = async () => {
    if (sessionId) {
      try {
        await axios.delete(`${API_URL}/api/agent/${sessionId}`)
      } catch (error) {
        console.error('Reset error:', error)
      }
    }
    setSessionId(null)
    setAgentStatus(null)
    setDesignPlan('')
    setFinalResults(null)
    setIsPolling(false)
  }

  return (
    <div className="App">
      <Toaster position="top-right" />
      
      <header className="app-header">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          🏠 AI Interior Design Agent
        </motion.h1>
        <p className="subtitle">Transform your empty room with AI-powered design</p>
      </header>

      <main className="app-main">
        <AnimatePresence mode="wait">
          {!sessionId ? (
            <motion.div
              key="upload"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.3 }}
            >
              <UploadSection onUpload={handleUpload} />
            </motion.div>
          ) : (
            <motion.div
              key="agent"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="agent-container"
            >
              <div className="agent-grid">
                <div className="left-panel">
                  <AgentProgress status={agentStatus} />
                  {finalResults && (
                    <button className="reset-button" onClick={resetAgent}>
                      Start New Design
                    </button>
                  )}
                </div>
                <div className="right-panel">
                  {designPlan && <DesignPlan markdown={designPlan} />}
                  {finalResults && <ResultsSection results={finalResults} />}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <footer className="app-footer">
                    <p>AI-Powered Interior Design Assistant</p>
      </footer>
    </div>
  )
}

export default App
