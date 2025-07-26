import React from 'react'
import { motion } from 'framer-motion'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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

interface ResultsSectionProps {
  results: FinalResults
}

const ResultsSection: React.FC<ResultsSectionProps> = ({ results }) => {
  return (
    <motion.div 
      className="results-section"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <h2>Final Design Results</h2>
      
      <div className="image-comparison">
        <div className="image-container">
          <h3>Original Room</h3>
          <img 
            src={`${API_URL}${results.original_image}`} 
            alt="Original room" 
          />
        </div>
        
        <div className="image-container">
          <h3>Designed Room</h3>
          <img 
            src={`${API_URL}${results.designed_image}`} 
            alt="Designed room" 
          />
        </div>
      </div>

      <div className="design-stats">
        <div className="stat-item">
          <h4>Total Cost Estimate</h4>
          <p className="stat-value">${results.total_cost_estimate.toFixed(2)}</p>
        </div>
        
        <div className="stat-item">
          <h4>Items Selected</h4>
          <p className="stat-value">{results.furniture_items.length}</p>
        </div>
        
        <div className="stat-item">
          <h4>Design Time</h4>
          <p className="stat-value">{results.completion_time.toFixed(1)}s</p>
        </div>
      </div>

      <div className="furniture-list">
        <h3>Selected Furniture</h3>
        <div className="furniture-grid">
          {results.furniture_items.map((item, index) => (
            <motion.div 
              key={index} 
              className="furniture-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              {item.image_url && (
                <div className="furniture-image">
                  <img 
                    src={`${API_URL}${item.image_url}`} 
                    alt={item.title}
                    onError={(e) => {
                      // Hide image if it fails to load
                      e.currentTarget.style.display = 'none'
                    }}
                  />
                </div>
              )}
              <h4>{item.title}</h4>
              {item.source && (
                <p className="furniture-source">from {item.source}</p>
              )}
              {item.category && (
                <p className="furniture-category">{item.category}</p>
              )}
              {item.price && (
                <p className="furniture-price">{item.price}</p>
              )}
              {item.product_rating && (
                <p className="furniture-rating">
                  {item.product_rating}⭐ ({item.product_reviews || 0} reviews)
                </p>
              )}
              {item.delivery && (
                <p className="furniture-delivery">{item.delivery}</p>
              )}
              {item.google_link && (
                <a 
                  href={item.google_link} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="product-link"
                >
                  View on Google Shopping →
                </a>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}

export default ResultsSection 