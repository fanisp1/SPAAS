'use client'

import { useState } from 'react'
import ResultsDisplay from './ResultsDisplay'
import ProtectionRulesConfig from './ProtectionRulesConfig'

interface BatchModeProps {
  onRunBatch: (batchFile: File, dataFile?: File, metadataFile?: File) => void
  processing: boolean
  error: string | null
  results: any
  protectionRules: {
    minFrequency: number
    dominanceN: number
    dominanceK: number
    pPercent: number
  }
  onProtectionRulesChange: (rules: any) => void
}

export default function BatchMode({ onRunBatch, processing, error, results, protectionRules, onProtectionRulesChange }: BatchModeProps) {
  const [batchFile, setBatchFile] = useState<File | null>(null)
  const [dataFile, setDataFile] = useState<File | null>(null)
  const [metadataFile, setMetadataFile] = useState<File | null>(null)
  const [parseResults, setParseResults] = useState<any>(null)
  const [parsing, setParsing] = useState(false)
  const [showDownloadMenu, setShowDownloadMenu] = useState(false)

  const handleBatchFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setBatchFile(file)
      setParseResults(null)
    }
  }

  const handleDataFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) setDataFile(file)
  }

  const handleMetadataFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) setMetadataFile(file)
  }

  const handleParseBatch = async () => {
    if (!batchFile) return

    setParsing(true)
    try {
      const formData = new FormData()
      formData.append('batch_file', batchFile)

      const response = await fetch('http://localhost:8000/batch/parse/', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error('Failed to parse batch file')
      }

      const data = await response.json()
      setParseResults(data)
      
      // Pre-fill protection rules from batch file if present
      if (data.summary?.safety_rules?.length > 0) {
        const newRules = { ...protectionRules }
        
        data.summary.safety_rules.forEach((rule: any) => {
          if (rule.type === 'Frequency' && rule.parameters.length >= 1) {
            newRules.minFrequency = rule.parameters[0]
          } else if (rule.type === 'Dominance' && rule.parameters.length >= 2) {
            newRules.dominanceN = rule.parameters[0]
            newRules.dominanceK = rule.parameters[1]
          }
        })
        
        onProtectionRulesChange(newRules)
      }
    } catch (err) {
      console.error('Parse error:', err)
    } finally {
      setParsing(false)
    }
  }

  const handleRunBatch = () => {
    if (batchFile) {
      onRunBatch(batchFile, dataFile || undefined, metadataFile || undefined)
    }
  }

  const currentStep = !batchFile ? 1 : !dataFile ? 2 : 3
  const isStep4Ready = batchFile && dataFile

  return (
    <div className="space-y-6">
      {/* Progress Steps */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          {/* Step 1 */}
          <div className="flex items-center flex-1">
            <div className={`flex items-center justify-center w-10 h-10 rounded-full font-bold ${
              currentStep >= 1 ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500'
            }`}>
              {batchFile ? '✓' : '1'}
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">Upload Batch File</p>
              <p className="text-xs text-gray-500">Instructions (.arb)</p>
            </div>
          </div>
          
          <div className="flex-1 h-1 mx-4 bg-gray-200">
            <div className={`h-full transition-all ${
              currentStep >= 2 ? 'bg-indigo-600 w-full' : 'bg-gray-200 w-0'
            }`} />
          </div>
          
          {/* Step 2 */}
          <div className="flex items-center flex-1">
            <div className={`flex items-center justify-center w-10 h-10 rounded-full font-bold ${
              currentStep >= 2 ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500'
            }`}>
              {dataFile ? '✓' : '2'}
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">Upload Data Files</p>
              <p className="text-xs text-gray-500">Statistical data (.tab)</p>
            </div>
          </div>
          
          <div className="flex-1 h-1 mx-4 bg-gray-200">
            <div className={`h-full transition-all ${
              currentStep >= 3 ? 'bg-indigo-600 w-full' : 'bg-gray-200 w-0'
            }`} />
          </div>
          
          {/* Step 3 */}
          <div className="flex items-center flex-1">
            <div className={`flex items-center justify-center w-10 h-10 rounded-full font-bold ${
              currentStep >= 3 ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500'
            }`}>
              {currentStep >= 3 ? '✓' : '3'}
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">Configure Rules</p>
              <p className="text-xs text-gray-500">Protection settings</p>
            </div>
          </div>
          
          <div className="flex-1 h-1 mx-4 bg-gray-200">
            <div className={`h-full transition-all ${
              isStep4Ready ? 'bg-indigo-600 w-full' : 'bg-gray-200 w-0'
            }`} />
          </div>
          
          {/* Step 4 */}
          <div className="flex items-center flex-1">
            <div className={`flex items-center justify-center w-10 h-10 rounded-full font-bold ${
              isStep4Ready ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500'
            }`}>
              4
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">Run Suppression</p>
              <p className="text-xs text-gray-500">Execute & Download</p>
            </div>
          </div>
        </div>
      </div>

      {/* Step 1: Batch File Upload */}
      <div className={`bg-white rounded-lg shadow-md p-6 border-2 ${
        currentStep === 1 ? 'border-indigo-600' : 'border-transparent'
      }`}>
        <div className="flex items-center mb-4">
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 font-bold mr-3">
            1
          </div>
          <h3 className="text-lg font-semibold text-gray-900">
            Upload Batch File (.arb) <span className="text-red-600 text-sm">*Required</span>
          </h3>
        </div>
        <p className="text-sm text-gray-600 mb-4">
          The batch file contains the suppression instructions and configuration.
        </p>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Batch File
            </label>
            <input
              type="file"
              accept=".arb"
              onChange={handleBatchFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
            />
            {batchFile && (
              <p className="mt-2 text-sm text-green-600">
                ✓ {batchFile.name}
              </p>
            )}
          </div>

          {batchFile && (
            <button
              onClick={handleParseBatch}
              disabled={parsing}
              className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300"
            >
              {parsing ? '🔍 Parsing...' : '🔍 Parse & Check Rules'}
            </button>
          )}
        </div>

        {/* Parse Results */}
        {parseResults && (
          <div className="mt-4 space-y-3">
            <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-2">Batch File Contents:</h4>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="font-medium">Data file:</span>{' '}
                  <span className="text-gray-700">
                    {parseResults.summary?.table_data_file || 'Not specified'}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Metadata file:</span>{' '}
                  <span className="text-gray-700">
                    {parseResults.summary?.metadata_file || 'Not specified'}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Method:</span>{' '}
                  <span className="text-gray-700">
                    {parseResults.summary?.suppression_method || 'HYPERCUBE'}
                  </span>
                </div>
                {parseResults.summary?.safety_rules?.length > 0 ? (
                  <div>
                    <span className="font-medium">Safety Rules:</span>
                    <ul className="ml-4 mt-1">
                      {parseResults.summary.safety_rules.map((rule: any, i: number) => (
                        <li key={i} className="text-gray-700">
                          {rule.type}({rule.parameters.join(', ')})
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  <div>
                    <span className="font-medium">Safety Rules:</span>{' '}
                    <span className="text-orange-600">None specified</span>
                  </div>
                )}
              </div>
            </div>
            
            {/* Safety Rules Status */}
            {parseResults.summary?.safety_rules?.length > 0 ? (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-start">
                  <svg className="w-5 h-5 text-green-600 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-green-900">
                      Safety rules found in batch file
                    </p>
                    <p className="text-xs text-green-700 mt-1">
                      Step 3 has been pre-filled with these values. You can modify them if needed.
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                <div className="flex items-start">
                  <svg className="w-5 h-5 text-orange-600 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-orange-900">
                      No safety rules in batch file
                    </p>
                    <p className="text-xs text-orange-700 mt-1">
                      <strong>Step 3 is required:</strong> Please configure protection rules before running.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Step 2: Upload data files */}
      <div className={`bg-white rounded-lg shadow-md p-6 border-2 ${
        currentStep === 2 ? 'border-indigo-600' : 'border-transparent'
      }`}>
        <div className="flex items-center mb-4">
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 font-bold mr-3">
            2
          </div>
          <h3 className="text-lg font-semibold text-gray-900">
            Upload Data Files
          </h3>
        </div>
        <p className="text-sm text-gray-600 mb-4">
          Upload your statistical data files here. The batch file (.arb) contains instructions, 
          while these files contain the actual data to be protected:
        </p>
        <ul className="text-sm text-gray-600 mb-4 ml-4 list-disc space-y-1">
          <li><strong>Data File (.tab)</strong> <span className="text-red-600">*Required</span>: Tabulated data with cells to be suppressed</li>
          <li><strong>Metadata File (.rda)</strong> <span className="text-gray-500">(Optional)</span>: Variable definitions and structure</li>
        </ul>
        
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data File (.tab)
            </label>
            <input
              type="file"
              accept=".tab"
              onChange={handleDataFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-gray-50 file:text-gray-700 hover:file:bg-gray-100"
            />
            {dataFile && (
              <p className="mt-1 text-sm text-green-600">✓ {dataFile.name}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Metadata File (.rda)
            </label>
            <input
              type="file"
              accept=".rda"
              onChange={handleMetadataFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-gray-50 file:text-gray-700 hover:file:bg-gray-100"
            />
            {metadataFile && (
              <p className="mt-1 text-sm text-green-600">✓ {metadataFile.name}</p>
            )}
          </div>
        </div>
      </div>

      {/* Step 3: Configure Protection Rules */}
      <div className={`bg-white rounded-lg shadow-md p-6 border-2 ${
        currentStep === 3 ? 'border-indigo-600' : 'border-transparent'
      }`}>
        <div className="flex items-center mb-4">
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 font-bold mr-3">
            3
          </div>
          <h3 className="text-lg font-semibold text-gray-900">
            Configure Protection Rules
          </h3>
        </div>
        <p className="text-sm text-gray-600 mb-4">
          Set thresholds for cell suppression. These rules override any rules in the batch file.
        </p>
        <ProtectionRulesConfig
          rules={protectionRules}
          onRulesChange={onProtectionRulesChange}
        />
      </div>

      {/* Step 4: Run Batch */}
      <div className={`bg-white rounded-lg shadow-md p-6 border-2 ${
        isStep4Ready ? 'border-indigo-600' : 'border-transparent'
      }`}>
        <div className="flex items-center mb-4">
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 font-bold mr-3">
            4
          </div>
          <h3 className="text-lg font-semibold text-gray-900">
            Execute Batch File
          </h3>
        </div>
        <button
          onClick={handleRunBatch}
          disabled={!batchFile || processing}
          className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
            !batchFile || processing
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
              Processing Batch...
            </span>
          ) : (
            '▶️ Execute Batch File'
          )}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">
            <span className="font-medium">Error:</span> {error}
          </p>
        </div>
      )}

      {/* Results Display */}
      {results && (
        <div className="space-y-4">
          <div className="border-2 border-green-500 rounded-lg p-2">
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 mb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="flex items-center justify-center w-10 h-10 rounded-full bg-green-600 text-white font-bold mr-3">
                    ✓
                  </div>
                  <h3 className="text-xl font-bold text-gray-900">
                    🎉 Batch Execution Complete!
                  </h3>
                </div>
                <div className="relative">
                  <button
                    onClick={() => setShowDownloadMenu(!showDownloadMenu)}
                    className="py-2 px-4 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors flex items-center gap-2"
                  >
                    📥 Download Results
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  
                  {showDownloadMenu && (
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
                      <button
                        onClick={async () => {
                          setShowDownloadMenu(false)
                          if (!dataFile) {
                            alert('Data file is required for Excel download')
                            return
                          }
                          
                          try {
                            const formData = new FormData()
                            formData.append('batch_file', batchFile)
                            formData.append('data_file', dataFile)
                            if (metadataFile) formData.append('metadata_file', metadataFile)
                            formData.append('min_frequency', protectionRules.minFrequency.toString())
                            formData.append('dominance_n', protectionRules.dominanceN.toString())
                            formData.append('dominance_k', protectionRules.dominanceK.toString())
                            formData.append('p_percent', protectionRules.pPercent.toString())
                            formData.append('output_format', 'excel')

                            const response = await fetch('http://localhost:8000/batch/download/', {
                              method: 'POST',
                              body: formData
                            })

                            if (response.ok) {
                              const blob = await response.blob()
                              const url = URL.createObjectURL(blob)
                              const a = document.createElement('a')
                              a.href = url
                              a.download = 'batch_suppressed.xlsx'
                              a.click()
                              URL.revokeObjectURL(url)
                            } else {
                              const errorText = await response.text()
                              console.error('Download failed:', errorText)
                              alert('Failed to download Excel file')
                            }
                          } catch (err) {
                            console.error('Download error:', err)
                            alert('Failed to download Excel file')
                          }
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-t-lg flex items-center gap-2"
                      >
                        📄 Excel (.xlsx)
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
                          a.download = 'batch_results.json'
                          a.click()
                          URL.revokeObjectURL(url)
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-b-lg flex items-center gap-2"
                      >
                        📊 JSON (.json)
                        <span className="text-xs text-gray-500">all data</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
            <ResultsDisplay results={results} />
          </div>
        </div>
      )}
    </div>
  )
}
