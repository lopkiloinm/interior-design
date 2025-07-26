import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { motion } from 'framer-motion'

interface DesignPlanProps {
  markdown: string
}

const DesignPlan: React.FC<DesignPlanProps> = ({ markdown }) => {
  return (
    <motion.div 
      className="design-plan"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h2>Design Plan</h2>
      <div className="markdown-content">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {markdown}
        </ReactMarkdown>
      </div>
    </motion.div>
  )
}

export default DesignPlan 