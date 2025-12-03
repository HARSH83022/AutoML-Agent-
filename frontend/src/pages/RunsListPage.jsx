import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Play, Clock, CheckCircle, XCircle, Loader } from 'lucide-react'
import { mlApi } from '../services/api.js'

export default function RunsListPage() {
  const [runs, setRuns] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  useEffect(() => {
    const fetchRuns = async () => {
      try {
        const data = await mlApi.listRuns()
        setRuns(data.runs || [])
        setLoading(false)
      } catch (err) {
        setError(err.message)
        setLoading(false)
      }
    }
    
    fetchRuns()
    
    // Refresh every 5 seconds
    const interval = setInterval(fetchRuns, 5000)
    return () => clearInterval(interval)
  }, [])
  
  const getStatusBadge = (status) => {
    const badges = {
      queued: { icon: Clock, color: 'bg-gray-100 text-gray-800', text: 'Queued' },
      running: { icon: Loader, color: 'bg-blue-100 text-blue-800', text: 'Running' },
      completed: { icon: CheckCircle, color: 'bg-green-100 text-green-800', text: 'Completed' },
      failed: { icon: XCircle, color: 'bg-red-100 text-red-800', text: 'Failed' }
    }
    
    const badge = badges[status] || badges.queued
    const Icon = badge.icon
    
    return (
      <span className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-sm font-medium ${badge.color}`}>
        <Icon size={16} className={status === 'running' ? 'animate-spin' : ''} />
        <span>{badge.text}</span>
      </span>
    )
  }
  
  const formatDate = (timestamp) => {
    if (!timestamp) return 'N/A'
    const date = new Date(timestamp * 1000)
    return date.toLocaleString()
  }
  
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
          <h2 className="text-xl font-bold text-red-900 mb-2">Error Loading Runs</h2>
          <p className="text-red-700">{error}</p>
        </div>
      </div>
    )
  }
  
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">All ML Runs</h1>
            <p className="text-gray-600">View and manage your machine learning experiments</p>
          </div>
          
          <Link to="/new" className="btn-primary flex items-center space-x-2">
            <Play size={18} />
            <span>Start New Run</span>
          </Link>
        </div>
      </div>
      
      {runs.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-gray-400 mb-4">
            <Play size={64} className="mx-auto" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No runs yet</h3>
          <p className="text-gray-600 mb-6">Start your first ML run to see it here</p>
          <Link to="/new" className="btn-primary inline-flex items-center space-x-2">
            <Play size={18} />
            <span>Start New Run</span>
          </Link>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Run ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created At
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {runs.map((run) => (
                  <tr key={run.run_id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {run.run_id.substring(0, 8)}...
                      </div>
                      <div className="text-xs text-gray-500">{run.run_id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(run.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(run.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <Link
                        to={`/runs/${run.run_id}`}
                        className="text-primary-600 hover:text-primary-900"
                      >
                        View Details →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      <div className="mt-6 text-center text-sm text-gray-500">
        Showing {runs.length} run{runs.length !== 1 ? 's' : ''}
      </div>
    </div>
  )
}
