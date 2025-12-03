import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const mlApi = {
  // Start a new ML run
  startRun: async (problemStatement, preferences = {}, uploadFile = null) => {
    // Backend expects JSON format with RunRequest model
    const payload = {
      problem_statement: problemStatement,
      preferences: preferences,
      user: {}
    }
    
    // If file is provided, we need to upload it first or pass the path
    // For now, we'll just send the JSON payload
    if (uploadFile) {
      // TODO: Handle file upload - for now just note it in user object
      payload.user.upload_path = uploadFile.name
    }
    
    const response = await api.post('/run', payload)
    return response.data
  },
  
  // Get run status
  getRunStatus: async (runId) => {
    const response = await api.get(`/status/${runId}`)
    return response.data
  },
  
  // List all runs
  listRuns: async () => {
    const response = await api.get('/runs')
    return response.data
  },
  
  // Parse problem statement or generate options
  parseProblemStatement: async (text, hint = '') => {
    const payload = {
      have_ps: text ? true : false,
      problem_statement: text,
      preferences: hint ? { hint } : {}
    }
    const response = await api.post('/ps', payload)
    return response.data
  },
  
  // Download artifact
  downloadArtifact: (filename) => {
    return `${API_BASE_URL}/artifacts/${filename}`
  },
  
  // Health check
  healthCheck: async () => {
    const response = await api.get('/health')
    return response.data
  },
}

export default api
