import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'

interface UploadSectionProps {
  onUpload: (file: File) => void
}

const UploadSection: React.FC<UploadSectionProps> = ({ onUpload }) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0])
    }
  }, [onUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp']
    },
    maxFiles: 1
  })

  const rootProps = getRootProps()

  return (
    <div className="upload-section">
      <motion.div
        className={`dropzone ${isDragActive ? 'active' : ''}`}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={rootProps.onClick}
        onKeyDown={rootProps.onKeyDown}
        onDragEnter={rootProps.onDragEnter}
        onDragOver={rootProps.onDragOver}
        onDragLeave={rootProps.onDragLeave}
        onDrop={rootProps.onDrop}
        role={rootProps.role}
        tabIndex={rootProps.tabIndex}
      >
        <input {...getInputProps()} />
        
        <div className="upload-content">
          <div className="upload-icon">📷</div>
          <h2>Upload Your Empty Room</h2>
          {isDragActive ? (
            <p>Drop the image here...</p>
          ) : (
            <>
              <p>Drag and drop an image here, or click to select</p>
              <p className="upload-hint">Supported formats: JPEG, PNG, GIF, WebP</p>
            </>
          )}
        </div>
      </motion.div>
      
      <div className="upload-info">
        <h3>How it works:</h3>
        <ol>
          <li>Upload a photo of your empty room</li>
          <li>Our AI agent analyzes the space</li>
          <li>It searches for furniture that fits your room</li>
          <li>Get a complete interior design plan!</li>
        </ol>
      </div>
    </div>
  )
}

export default UploadSection 