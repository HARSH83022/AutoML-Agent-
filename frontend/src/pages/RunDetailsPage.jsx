import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Download, CheckCircle, XCircle, Loader, Clock } from 'lucide-react'
import { mlApi } from '../services/api.js'

export default function RunDetailsPage() {
  const { runId } = useParams()
  const [runData, setRunData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  useEffect(() => {
    let interval
    
    const fetchStatus = async () => {
      try {
        const data = await mlApi.getRunStatus(runId)
        setRunData(data)
        setLoading(false)
        
        if (data.status === 'completed' || data.status === 'failed') {
          if (interval) clearInterval(interval)
        }
      } catch (err) {
        setError(err.message)
        setLoading(false)
        if (interval) clearInterval(interval)
      }
    }
    
    fetchStatus()
    interval = setInterval(fetchStatus, 2000)
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [runId])
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader className="animate-spin text-primary-600" size={48} />
      </div>
    )
  }
  
  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="card bg-red-50 border border-red-200">
          <XCircle className="text-red-600 mb-2" size={32} />
          <h2 className="text-xl font-bold text-red-900 mb-2">Error Loading Run</h2>
          <p className="text-red-700">{error}</p>
        </div>
      </div>
    )
  }
  
  const { status, state, last_error, log_tail, artifacts } = runData || {}
  const metrics = state?.metrics || {}
  const phase = state?.phase || 'initializing'
  
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <Link to="/runs" className="flex items-center space-x-2 text-primary-600 hover:text-primary-700 mb-4">
          <ArrowLeft size={20} />
          <span>Back to All Runs</span>
        </Link>
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Run Details</h1>
            <p className="text-gray-600">Run ID: {runId}</p>
          </div>
          
          <div className="flex items-center space-x-2">
            {status === 'queued' && (
              <span className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-800 rounded-lg">
                <Clock size={18} />
                <span>Queued</span>
              </span>
            )}
            {status === 'running' && (
              <span className="flex items-center space-x-2 px-4 py-2 bg-blue-100 text-blue-800 rounded-lg">
                <Loader className="animate-spin" size={18} />
                <span>Running</span>
              </span>
            )}
            {status === 'completed' && (
              <span className="flex items-center space-x-2 px-4 py-2 bg-green-100 text-green-800 rounded-lg">
                <CheckCircle size={18} />
                <span>Completed</span>
              </span>
            )}
            {status === 'failed' && (
              <span className="flex items-center space-x-2 px-4 py-2 bg-red-100 text-red-800 rounded-lg">
                <XCircle size={18} />
                <span>Failed</span>
              </span>
            )}
          </div>
        </div>
      </div>
      
      {/* Current Phase */}
      <div className="card mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-3">Current Phase</h2>
        <div className="flex items-center space-x-3">
          <div className="flex-1">
            <div className="text-lg font-medium text-gray-900 capitalize">{phase.replace(/_/g, ' ')}</div>
            <div className="text-sm text-gray-500 mt-1">
              {status === 'running' && 'Processing...'}
              {status === 'completed' && 'All steps completed successfully'}
              {status === 'failed' && 'Run failed'}
              {status === 'queued' && 'Waiting to start'}
            </div>
          </div>
          {status === 'running' && (
            <Loader className="animate-spin text-primary-600" size={24} />
          )}
        </div>
      </div>
      
      {/* Dataset Information */}
      {(state?.dataset_source || state?.dataset_source_name) && (
        <div className="card mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Dataset Information</h2>
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-600 font-medium mb-1">Source</div>
                <div className="text-lg font-bold text-gray-900">{state.dataset_source || 'Unknown'}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600 font-medium mb-1">Dataset Name</div>
                <div className="text-lg font-semibold text-gray-900">{state.dataset_source_name || 'Unknown'}</div>
              </div>
            </div>
            {state?.dataset_source_url && (
              <div className="mt-3 pt-3 border-t border-blue-200">
                <a 
                  href={state.dataset_source_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center space-x-1"
                >
                  <span>View Dataset Source</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Trained Models */}
      {state?.trained_models && state.trained_models.length > 0 && (
        <div className="card mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Trained Models</h2>
          <div className="space-y-2">
            {state.trained_models
              .sort((a, b) => (b.score || 0) - (a.score || 0))
              .map((model, index) => (
              <div 
                key={index} 
                className={`flex items-center justify-between p-4 rounded-lg border-2 transition-all ${
                  model.name === state.best_model 
                    ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-300' 
                    : 'bg-gray-50 border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-3">
                  {model.name === state.best_model && (
                    <svg className="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  )}
                  <div>
                    <div className="font-semibold text-gray-900">{model.name}</div>
                    {model.name === state.best_model && (
                      <div className="text-xs text-green-600 font-medium">Best Performing Model</div>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-600">Score</div>
                  <div className="text-xl font-bold text-gray-900">
                    {typeof model.score === 'number' ? model.score.toFixed(4) : 'N/A'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Best Model & Metrics */}
      {Object.keys(metrics).length > 0 && (
        <div className="card mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Model Performance</h2>
            {state?.best_model && (
              <div className="flex items-center space-x-2 px-4 py-2 bg-primary-100 text-primary-800 rounded-lg">
                <span className="text-sm font-medium">Best Model:</span>
                <span className="text-lg font-bold">{state.best_model}</span>
              </div>
            )}
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(metrics).map(([key, value]) => (
              <div key={key} className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600 capitalize">{key.replace(/_/g, ' ')}</div>
                <div className="text-2xl font-bold text-gray-900 mt-1">
                  {typeof value === 'number' ? value.toFixed(4) : value || 'N/A'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Error Message */}
      {last_error && (
        <div className="card bg-red-50 border border-red-200 mb-6">
          <h2 className="text-xl font-semibold text-red-900 mb-3">Error</h2>
          <p className="text-red-700 font-mono text-sm">{last_error}</p>
        </div>
      )}
      
      {/* Artifacts */}
      {artifacts && artifacts.length > 0 && (
        <div className="card mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Artifacts</h2>
          <div className="space-y-2">
            {artifacts.map((artifact, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <span className="text-sm font-medium text-gray-900">{artifact}</span>
                <a
                  href={`/api/artifacts/${artifact}`}
                  download
                  className="flex items-center space-x-1 text-primary-600 hover:text-primary-700"
                >
                  <Download size={16} />
                  <span className="text-sm">Download</span>
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Logs */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Logs</h2>
        <div className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm overflow-x-auto max-h-96 overflow-y-auto">
          <pre className="whitespace-pre-wrap">{log_tail || 'No logs available yet...'}</pre>
        </div>
      </div>
    </div>
  )
}
