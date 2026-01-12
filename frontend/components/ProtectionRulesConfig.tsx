'use client'

interface ProtectionRules {
  minFrequency: number
  dominanceN: number
  dominanceK: number
  pPercent: number
}

interface ProtectionRulesConfigProps {
  rules: ProtectionRules
  onRulesChange: (rules: ProtectionRules) => void
}

export default function ProtectionRulesConfig({ rules, onRulesChange }: ProtectionRulesConfigProps) {
  const handleChange = (field: keyof ProtectionRules, value: number) => {
    onRulesChange({
      ...rules,
      [field]: value
    })
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        🔒 Protection Rules
      </h3>
      
      <div className="space-y-4">
        {/* Frequency Rule */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Minimum Frequency
            <span className="ml-2 text-xs text-gray-500">(cells &lt; this value will be suppressed)</span>
          </label>
          <input
            type="number"
            min="1"
            max="100"
            value={rules.minFrequency}
            onChange={(e) => handleChange('minFrequency', parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500 mt-1">
            Current: {rules.minFrequency} (Higher = more suppressions)
          </p>
        </div>

        {/* Dominance N */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Dominance N
            <span className="ml-2 text-xs text-gray-500">(top N contributors)</span>
          </label>
          <select
            value={rules.dominanceN}
            onChange={(e) => handleChange('dominanceN', parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          >
            <option value={1}>1 (Single dominance)</option>
            <option value={2}>2 (Top 2 dominance)</option>
            <option value={3}>3 (Top 3 dominance)</option>
          </select>
        </div>

        {/* Dominance K% */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Dominance Threshold (%)
            <span className="ml-2 text-xs text-gray-500">(top N must not exceed this %)</span>
          </label>
          <div className="flex items-center space-x-3">
            <input
              type="range"
              min="50"
              max="95"
              step="5"
              value={rules.dominanceK}
              onChange={(e) => handleChange('dominanceK', parseFloat(e.target.value))}
              className="flex-1"
            />
            <span className="text-sm font-medium text-indigo-600 w-16 text-right">
              {rules.dominanceK}%
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Lower = stricter (more suppressions)
          </p>
        </div>

        {/* P-Percent Rule */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            P-Percent Rule (%)
            <span className="ml-2 text-xs text-gray-500">(estimation threshold)</span>
          </label>
          <div className="flex items-center space-x-3">
            <input
              type="range"
              min="5"
              max="20"
              step="1"
              value={rules.pPercent}
              onChange={(e) => handleChange('pPercent', parseFloat(e.target.value))}
              className="flex-1"
            />
            <span className="text-sm font-medium text-indigo-600 w-16 text-right">
              {rules.pPercent}%
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Lower = stricter (more suppressions)
          </p>
        </div>
      </div>

      {/* Reset Button */}
      <button
        onClick={() => onRulesChange({
          minFrequency: 10,
          dominanceN: 1,
          dominanceK: 80.0,
          pPercent: 10.0
        })}
        className="mt-4 w-full py-2 px-4 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
      >
        Reset to Defaults
      </button>
    </div>
  )
}
