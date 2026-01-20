'use client'

import { useRouter } from 'next/navigation'
import { useState } from 'react'

const methods = [
  {
    id: 'primary',
    name: 'Primary Suppression',
    icon: '🛡️',
    description: 'Eurostat-compliant primary confidentiality identification and suppression',
    status: 'available',
    color: 'from-cyan-500 to-blue-600'
  },
  {
    id: 'hypercube',
    name: 'Hypercube',
    icon: '🔷',
    description: 'Graph-based optimization for minimal secondary suppressions',
    status: 'available',
    color: 'from-blue-500 to-indigo-600'
  },
  {
    id: 'modular',
    name: 'Modular',
    icon: '🧩',
    description: 'Table decomposition with independent sub-table protection',
    status: 'coming-soon',
    color: 'from-purple-500 to-pink-600'
  },
  {
    id: 'optimal',
    name: 'Optimal',
    icon: '🎯',
    description: 'Linear programming for optimal suppression patterns',
    status: 'coming-soon',
    color: 'from-green-500 to-emerald-600'
  },
  {
    id: 'network',
    name: 'Network',
    icon: '🌐',
    description: 'Network flow optimization for cell suppression',
    status: 'coming-soon',
    color: 'from-orange-500 to-red-600'
  }
]

export default function MethodsPage() {
  const router = useRouter()
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)

  const handleMethodClick = (methodId: string, status: string) => {
    if (status === 'available') {
      router.push(`/methods/${methodId}`)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              🔒 SPAAS
            </h1>
            <p className="text-lg text-gray-700">
              Statistical Package for Automated Anonymization Software
            </p>
            <p className="text-sm text-gray-600 mt-1">
              Select a suppression method to begin
            </p>
          </div>
        </div>
      </header>

      {/* 3D Card Grid */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {methods.map((method, index) => (
            <div
              key={method.id}
              className="relative group perspective-1000"
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              <div
                className={`
                  relative h-80 rounded-2xl cursor-pointer
                  transform transition-all duration-500 ease-out
                  ${hoveredIndex === index ? 'scale-110 -translate-y-4' : 'scale-100'}
                  ${method.status === 'coming-soon' ? 'opacity-75' : ''}
                `}
                onClick={() => handleMethodClick(method.id, method.status)}
                style={{
                  transformStyle: 'preserve-3d',
                  transform: hoveredIndex === index 
                    ? 'rotateY(5deg) rotateX(-5deg)' 
                    : 'rotateY(0deg) rotateX(0deg)'
                }}
              >
                
                {/* Card */}
                <div className="relative h-full rounded-2xl p-6 bg-white shadow-xl overflow-hidden border border-gray-200">

                  {/* Content */}
                  <div className="relative h-full flex flex-col justify-between z-10">
                    {/* Icon */}
                    <div className="text-center">
                      <div className={`
                        text-8xl mb-4 inline-block
                        transform transition-transform duration-500
                        ${hoveredIndex === index ? 'scale-110 rotate-12' : 'scale-100 rotate-0'}
                      `}>
                        {method.icon}
                      </div>
                      
                      {method.status === 'coming-soon' && (
                        <div className="inline-block px-3 py-1 rounded-full text-xs font-bold bg-gray-100 text-gray-600 border border-gray-300">
                          Coming Soon
                        </div>
                      )}
                    </div>

                    {/* Text */}
                    <div className="text-center">
                      <h3 className="text-2xl font-bold text-gray-900 mb-3">
                        {method.name}
                      </h3>
                      <p className="text-sm text-gray-600 leading-relaxed">
                        {method.description}
                      </p>
                    </div>

                    {/* Action */}
                    <div className="text-center">
                      {method.status === 'available' ? (
                        <div className="inline-flex items-center text-indigo-600 font-semibold group-hover:gap-3 gap-2 transition-all">
                          <span>Launch Method</span>
                          <svg 
                            className="w-5 h-5 transform group-hover:translate-x-1 transition-transform" 
                            fill="none" 
                            stroke="currentColor" 
                            viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                          </svg>
                        </div>
                      ) : (
                        <div className="text-gray-400 text-sm">
                          Under Construction
                        </div>
                      )}
                    </div>
                  </div>

                </div>
              </div>
            </div>
          ))}
        </div>

      </main>

      {/* Footer */}
      <footer className="mt-12 bg-white/80 backdrop-blur-sm border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            SPAAS Modernized - Built with Python + Next.js | Eurostat Project
          </p>
        </div>
      </footer>
    </div>
  )
}
