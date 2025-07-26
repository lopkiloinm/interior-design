import React from 'react'
import { motion } from 'framer-motion'

interface AgentMessage {
  timestamp: string
  message: string
}

interface AgentStatus {
  status: string
  current_step: string
  steps_completed: string[]
  progress_percentage: number
  messages: AgentMessage[]
  errors: string[]
}

interface AgentProgressProps {
  status: AgentStatus | null
}

const AgentProgress: React.FC<AgentProgressProps> = ({ status }) => {
  if (!status) {
    return (
      <div className="agent-progress">
        <h2>Waiting for agent to start...</h2>
      </div>
    )
  }

  const statusEmoji: { [key: string]: string } = {
    idle: '💤',
    analyzing: '🔍',
    planning: '📝',
    shopping: '🛍️',
    designing: '🎨',
    completed: '✅',
    error: '❌'
  }

  return (
    <div className="agent-progress">
      <h2>Agent Progress</h2>
      
      <div className="status-header">
        <span className="status-emoji">{statusEmoji[status.status] || '⏳'}</span>
        <h3>{status.current_step}</h3>
      </div>

      <div className="progress-bar-container">
        <motion.div 
          className="progress-bar"
          initial={{ width: 0 }}
          animate={{ width: `${status.progress_percentage}%` }}
          transition={{ duration: 0.5 }}
        />
        <span className="progress-text">{Math.round(status.progress_percentage)}%</span>
      </div>

      <div className="steps-list">
        <h4>Steps Completed:</h4>
        <ul>
          {status.steps_completed.map((step, index) => (
            <motion.li 
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              ✓ {step}
            </motion.li>
          ))}
        </ul>
      </div>

      <div className="messages-log">
        <h4>Activity Log:</h4>
        <div className="messages-container">
          {status.messages.slice(-5).map((msg, index) => (
            <motion.div 
              key={index} 
              className="message-item"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <span className="message-time">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </span>
              <span className="message-text">{msg.message}</span>
            </motion.div>
          ))}
        </div>
      </div>

      {status.errors.length > 0 && (
        <div className="errors-section">
          <h4>Errors:</h4>
          {status.errors.map((error, index) => (
            <div key={index} className="error-item">
              ⚠️ {error}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default AgentProgress 