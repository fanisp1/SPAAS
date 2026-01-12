'use client'

interface ResultsDisplayProps {
  results: {
    status: string
    method: string
    statistics: {
      total_cells: number
      primary_suppressions: number
      secondary_suppressions: number
      total_suppressions: number
      suppression_rate: number
      primary_cells?: Array<{row: number, col: number}>
      secondary_cells?: Array<{row: number, col: number}>
    }
    suppressed_data: Array<Record<string, any>>
    column_names: string[]
  }
}

export default function ResultsDisplay({ results }: ResultsDisplayProps) {
  const { statistics, suppressed_data, column_names } = results
  
  // Create sets for O(1) lookup - separate primary and secondary
  const primaryCellsSet = new Set(
    (statistics.primary_cells || []).map(cell => `${cell.row}_${cell.col}`)
  )
  const secondaryCellsSet = new Set(
    (statistics.secondary_cells || []).map(cell => `${cell.row}_${cell.col}`)
  )

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-md p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Total Cells</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {statistics.total_cells}
          </p>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Primary</p>
          <p className="text-2xl font-bold text-orange-600 mt-1">
            {statistics.primary_suppressions}
          </p>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Secondary</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">
            {statistics.secondary_suppressions}
          </p>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Total Suppressed</p>
          <p className="text-2xl font-bold text-indigo-600 mt-1">
            {statistics.total_suppressions}
          </p>
        </div>
      </div>

      {/* Suppression Rate */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Suppression Rate
        </h3>
        <div className="relative pt-1">
          <div className="flex mb-2 items-center justify-between">
            <div>
              <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-indigo-600 bg-indigo-200">
                Protection Applied
              </span>
            </div>
            <div className="text-right">
              <span className="text-xs font-semibold inline-block text-indigo-600">
                {(statistics.suppression_rate * 100).toFixed(2)}%
              </span>
            </div>
          </div>
          <div className="overflow-hidden h-4 mb-4 text-xs flex rounded-full bg-indigo-100">
            <div
              style={{ width: `${statistics.suppression_rate * 100}%` }}
              className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-indigo-600 transition-all duration-500"
            ></div>
          </div>
        </div>
        <p className="text-sm text-gray-600">
          {statistics.total_suppressions} out of {statistics.total_cells} cells suppressed for privacy protection
        </p>
      </div>

      {/* Suppressed Data Table */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Suppressed Data Preview
          </h3>
          <span className="text-xs text-gray-500">
            Showing {Math.min(suppressed_data.length, 10)} of {suppressed_data.length} rows
          </span>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  #
                </th>
                {column_names.map((col, idx) => (
                  <th
                    key={idx}
                    className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {suppressed_data.slice(0, 10).map((row, rowIdx) => (
                <tr key={rowIdx} className="hover:bg-gray-50">
                  <td className="px-3 py-3 whitespace-nowrap text-sm font-medium text-gray-500">
                    {rowIdx + 1}
                  </td>
                  {column_names.map((col, frontendColIdx) => {
                    const value = row[col]
                    const cellKey = `${rowIdx}_${frontendColIdx}`
                    const isPrimary = primaryCellsSet.has(cellKey)
                    const isSecondary = secondaryCellsSet.has(cellKey)
                    
                    let cellClass = 'text-gray-900'
                    if (isPrimary) {
                      cellClass = 'font-bold text-blue-600'  // Blue for primary
                    } else if (isSecondary) {
                      cellClass = 'font-bold text-red-600'  // Red for secondary
                    }
                    
                    return (
                      <td
                        key={frontendColIdx}
                        className={`px-3 py-3 whitespace-nowrap text-sm ${cellClass}`}
                      >
                        {value === null || value === undefined ? '-' : String(value)}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {suppressed_data.length > 10 && (
          <p className="text-xs text-gray-500 mt-4 text-center">
            Download the complete data to see all {suppressed_data.length} rows
          </p>
        )}
      </div>

      {/* Legend */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-yellow-900 mb-2">
          📊 Legend
        </h4>
        <div className="space-y-1 text-xs text-yellow-800">
          <p>• <span className="font-bold text-blue-600 px-1">Blue numbers</span> = Primary suppressions (violate protection rules)</p>
          <p>• <span className="font-bold text-red-600 px-1">Red numbers</span> = Secondary suppressions (prevent back-calculation)</p>
          <p>• Regular numbers = Non-sensitive cells (safe to publish)</p>
        </div>
      </div>
    </div>
  )
}
