'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import FileUpload from '@/components/FileUpload'
import ProtectionRulesConfig from '@/components/ProtectionRulesConfig'
import ResultsDisplay from '@/components/ResultsDisplay'
import BatchMode from '@/components/BatchMode'

export default function Home() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<'direct' | 'batch'>('direct')
  const [file, setFile] = useState<File | null>(null)
  const [processing, setProcessing] = useState(false)
  const [batchProcessing, setBatchProcessing] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [batchResults, setBatchResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [batchError, setBatchError] = useState<string | null>(null)
  const [showDownloadMenu, setShowDownloadMenu] = useState(false)

  const [protectionRules, setProtectionRules] = useState({
    minFrequency: 3,
    dominanceN: 1,
    dominanceK: 80.0,
    pPercent: 10.0
  })

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile)
    setResults(null)
    setError(null)
  }

  const handleProcessFile = async () => {
    if (!file) {
      setError('Please select a file first')
      return
    }

    setProcessing(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('min_frequency', protectionRules.minFrequency.toString())
      formData.append('dominance_n', protectionRules.dominanceN.toString())
      formData.append('dominance_k', protectionRules.dominanceK.toString())
      formData.append('p_percent', protectionRules.pPercent.toString())

      const response = await fetch('http://localhost:8000/suppress/hypercube/', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to process file')
      }

      const data = await response.json()
      setResults(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setProcessing(false)
    }
  }

  const handleDownload = async () => {
    if (!file) {
      setError('No file uploaded')
      return
    }

    setError(null)
    
    try {
      // Show downloading state
      const downloadButton = document.querySelector('[data-download-button]') as HTMLButtonElement
      if (downloadButton) {
        downloadButton.disabled = true
        downloadButton.textContent = '⏳ Downloading...'
      }

      const formData = new FormData()
      formData.append('file', file)
      formData.append('min_frequency', protectionRules.minFrequency.toString())
      formData.append('dominance_n', protectionRules.dominanceN.toString())
      formData.append('dominance_k', protectionRules.dominanceK.toString())
      formData.append('p_percent', protectionRules.pPercent.toString())
      formData.append('output_format', 'excel')

      console.log('Requesting download...')
      const response = await fetch('http://localhost:8000/suppress/hypercube/download/', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorText = await response.text()
        console.error('Download failed:', errorText)
        throw new Error(`Download failed: ${response.status} ${response.statusText}`)
      }

      console.log('Creating blob...')
      const blob = await response.blob()
      console.log('Blob created, size:', blob.size)
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      // Remove existing extension and add .xlsx
      const baseName = file.name.replace(/\.[^.]+$/, '')
      a.download = `suppressed_${baseName}.xlsx`
      a.style.display = 'none'
      document.body.appendChild(a)
      
      console.log('Triggering download...')
      a.click()
      
      // Cleanup
      setTimeout(() => {
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        console.log('Download complete!')
      }, 100)
      
      // Reset button
      if (downloadButton) {
        downloadButton.disabled = false
        downloadButton.textContent = '📥 Download Suppressed Data'
      }
      
    } catch (err) {
      console.error('Download error:', err)
      setError(err instanceof Error ? err.message : 'Failed to download file')
      
      // Reset button on error
      const downloadButton = document.querySelector('[data-download-button]') as HTMLButtonElement
      if (downloadButton) {
        downloadButton.disabled = false
        downloadButton.textContent = '📥 Download Suppressed Data'
      }
    }
  }

  const handleRunBatch = async (batchFile: File, dataFile?: File, metadataFile?: File) => {
    setBatchProcessing(true)
    setBatchError(null)
    setBatchResults(null)

    try {
      const formData = new FormData()
      formData.append('batch_file', batchFile)
      if (dataFile) formData.append('data_file', dataFile)
      if (metadataFile) formData.append('metadata_file', metadataFile)
      
      formData.append('min_frequency', protectionRules.minFrequency.toString())
      formData.append('dominance_n', protectionRules.dominanceN.toString())
      formData.append('dominance_k', protectionRules.dominanceK.toString())
      formData.append('p_percent', protectionRules.pPercent.toString())

      const response = await fetch('http://localhost:8000/batch/execute/', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to execute batch file')
      }

      const data = await response.json()
      setBatchResults(data)
    } catch (err) {
      setBatchError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setBatchProcessing(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/methods')}
                className="text-gray-500 hover:text-gray-700 transition-colors"
                title="Back to Methods"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </button>
              <div>
                <h1 
                  className="text-3xl font-bold text-gray-900 cursor-pointer hover:text-indigo-600 transition-colors"
                  onClick={() => router.push('/methods')}
                  title="Back to Methods"
                >
                  🔒 SPAAS
                </h1>
                <p className="text-sm text-gray-600 mt-1">
                  Statistical Package for Automated Anonymization Software
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800">
                Hypercube Method {activeTab === 'batch' && '- Batch Mode'}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Mode Tabs */}
        <div className="bg-white rounded-lg shadow-md mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('direct')}
                className={`py-4 px-6 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'direct'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                📊 Direct Mode
              </button>
              <button
                onClick={() => setActiveTab('batch')}
                className={`py-4 px-6 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'batch'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                📦 Batch Mode
              </button>
            </nav>
          </div>
        </div>
        {activeTab === 'direct' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Upload & Configuration */}
          <div className="lg:col-span-1 space-y-6">
            {/* File Upload */}
            <FileUpload 
              onFileSelect={handleFileSelect}
              selectedFile={file}
            />

            {/* Protection Rules Configuration */}
            <ProtectionRulesConfig
              rules={protectionRules}
              onRulesChange={setProtectionRules}
            />

            {/* Action Buttons */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Actions
              </h3>
              <div className="space-y-3">
                <button
                  onClick={handleProcessFile}
                  disabled={!file || processing}
                  className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                    !file || processing
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-indigo-600 text-white hover:bg-indigo-700'
                  }`}
                >
                  {processing ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </span>
                  ) : (
                    '🚀 Run Hypercube Suppression'
                  )}
                </button>

                {results && (
                  <div className="relative">
                    <button
                      onClick={() => setShowDownloadMenu(!showDownloadMenu)}
                      className="w-full py-3 px-4 rounded-lg font-medium bg-green-600 text-white hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
                    >
                      📥 Download Suppressed Data
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    
                    {showDownloadMenu && (
                      <div className="absolute left-0 right-0 mt-2 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
                        <button
                          data-download-button
                          onClick={() => {
                            setShowDownloadMenu(false)
                            handleDownload()
                          }}
                          className="w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-100 rounded-t-lg flex items-center justify-between"
                        >
                          <span className="flex items-center gap-2">
                            📄 Excel (.xlsx)
                          </span>
                          <span className="text-xs text-gray-500">with colors</span>
                        </button>
                        <button
                          onClick={() => {
                            setShowDownloadMenu(false)
                            const dataStr = JSON.stringify(results, null, 2)
                            const blob = new Blob([dataStr], { type: 'application/json' })
                            const url = URL.createObjectURL(blob)
                            const a = document.createElement('a')
                            a.href = url
                            a.download = 'suppressed_results.json'
                            a.click()
                            URL.revokeObjectURL(url)
                          }}
                          className="w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-100 rounded-b-lg flex items-center justify-between"
                        >
                          <span className="flex items-center gap-2">
                            📊 JSON (.json)
                          </span>
                          <span className="text-xs text-gray-500">all data</span>
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Method Info */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-blue-900 mb-2">
                ℹ️ About Hypercube Method
              </h4>
              <p className="text-xs text-blue-800">
                The hypercube method uses graph-based optimization to find the minimal 
                set of secondary suppressions needed to protect sensitive cells, 
                balancing privacy protection with data utility.
              </p>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-2">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">Error</h3>
                    <p className="text-sm text-red-700 mt-1">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {results ? (
              <ResultsDisplay results={results} />
            ) : (
              <div className="bg-white rounded-lg shadow-md p-12 text-center">
                <div className="mx-auto h-24 w-24 text-gray-400 mb-4">
                  <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Results Yet
                </h3>
                <p className="text-gray-600 text-sm">
                  Upload a file and click "Run Hypercube Suppression" to see results here.
                </p>
              </div>
            )}
          </div>
        </div>
        ) : (
          <BatchMode 
            onRunBatch={handleRunBatch}
            processing={batchProcessing}
            error={batchError}
            results={batchResults}
            protectionRules={protectionRules}
            onProtectionRulesChange={setProtectionRules}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="mt-12 bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            SPAAS Modernized - Built with Python + Next.js | 
            <span className="ml-2 text-indigo-600">Hypercube Method Active</span>
          </p>
        </div>
      </footer>
    </div>
  )
}
