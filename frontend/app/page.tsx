'use client'

import { useState, useEffect } from 'react'

export default function Home() {
  const [backendStatus, setBackendStatus] = useState<string>('Checking...')

  useEffect(() => {
    // Test backend connection
    fetch('http://localhost:8000/health')
      .then(response => response.json())
      .then(data => setBackendStatus('Connected'))
      .catch(() => setBackendStatus('Not connected'))
  }, [])

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="text-center space-y-6">
        <h1 className="text-4xl font-bold text-gray-900">
          Next.js + FastAPI Template
        </h1>
        
        <p className="text-xl text-gray-600 max-w-md">
          A minimal template project to get you started building full-stack applications.
        </p>

        <div className="bg-gray-100 rounded-lg p-4">
          <p className="text-sm text-gray-700">
            Backend Status: <span className="font-mono">{backendStatus}</span>
          </p>
        </div>

        <div className="space-y-2 text-sm text-gray-500">
          <p>Frontend running on: <code className="bg-gray-100 px-2 py-1 rounded">http://localhost:3000</code></p>
          <p>Backend running on: <code className="bg-gray-100 px-2 py-1 rounded">http://localhost:8000</code></p>
        </div>
      </div>
    </main>
  )
} 