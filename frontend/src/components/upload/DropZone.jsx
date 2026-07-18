import { useState, useRef } from 'react'
import Icon from '../shared/Icon.jsx'

export default function DropZone({ onFileSelected, isLoading }) {
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef(null)

  function handleDrop(e) {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files?.[0]
    if (file) onFileSelected(file)
  }

  function handleFileInputChange(e) {
    const file = e.target.files?.[0]
    if (file) onFileSelected(file)
  }

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      className={`
        border-2 border-dashed rounded-xl p-xl flex flex-col items-center justify-center text-center
        min-h-[320px] cursor-pointer transition-all
        ${isDragging ? 'border-primary bg-primary/5 scale-[1.01]' : 'border-outline-variant bg-surface-container-lowest'}
        ${isLoading ? 'opacity-60 pointer-events-none' : ''}
      `}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".csv"
        className="hidden"
        onChange={handleFileInputChange}
      />

      {isLoading ? (
        <>
          <div className="w-16 h-16 border-4 border-outline-variant border-t-primary rounded-full animate-spin mb-lg" />
          <h2 className="font-headline-md text-headline-md text-on-surface">Processing your statement...</h2>
          <p className="text-on-surface-variant font-body-md mt-xs">Cleaning, categorizing, and detecting subscriptions.</p>
        </>
      ) : (
        <>
          <div className="w-20 h-20 bg-primary rounded-2xl flex items-center justify-center mb-lg">
            <Icon name="cloud_upload" className="text-on-primary text-4xl" filled />
          </div>
          <h2 className="font-headline-md text-headline-md mb-sm text-on-surface">Drag &amp; Drop your statement here</h2>
          <p className="text-on-surface-variant font-body-md mb-lg max-w-md">
            Or click to browse. Only .CSV bank/UPI exports are supported right now.
          </p>
        </>
      )}
    </div>
  )
}