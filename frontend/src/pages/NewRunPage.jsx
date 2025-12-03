import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Play, Upload, Loader } from 'lucide-react'
import { mlApi } from '../services/api.js'

export default function NewRunPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [hasPS, setHasPS] = useState(null)
  const [generatingPS, setGeneratingPS] = useState(false)
  const [psOptions, setPsOptions] = useState([])
  const [formData, setFormData] = useState({
    problemStatement: '',
    trainingBudget: 10,  // Increased default from 5 to 10 minutes for better accuracy
    primaryMetric: 'f1',
    file: null,
    hint: ''
  })
  
  const handleGeneratePS = async () => {
    setGeneratingPS(true)
    try {
      const response = await mlApi.parseProblemStatement('', formData.hint)
      if (response.status === 'ok' && response.ps_options) {
        setPsOptions(response.ps_options)
      } else if (response.mode === 'generated_options' && response.ps_options) {
        setPsOptions(response.ps_options)
      }
    } catch (error) {
      console.error('Failed to generate PS:', error)
      alert('Failed to generate problem statements. Please try again.')
    } finally {
      setGeneratingPS(false)
    }
  }

  const handleSelectOption = (option) => {
    const text = option.statement || option.raw_text || JSON.stringify(option)
    setFormData({ ...formData, problemStatement: text })
    setPsOptions([])
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const preferences = {
        training_budget_minutes: formData.trainingBudget,
        primary_metric: formData.primaryMetric
      }
      
      const response = await mlApi.startRun(
        formData.problemStatement,
        preferences,
        formData.file
      )
      
      navigate(`/runs/${response.run_id}`)
    } catch (error) {
      console.error('Failed to start run:', error)
      alert('Failed to start run. Please try again.')
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Start New ML Run</h1>
        <p className="text-gray-600">
          Describe your machine learning problem and let our AI agents handle the rest
        </p>
      </div>
      
      {/* Step 1: Ask if user has PS */}
      {hasPS === null && (
        <div className="card space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">Do you have a problem statement?</h2>
          <p className="text-gray-600">Choose how you want to proceed</p>
          <div className="flex space-x-4">
            <button
              type="button"
              onClick={() => setHasPS(true)}
              className="btn-primary flex-1"
            >
              Yes - I have one
            </button>
            <button
              type="button"
              onClick={() => setHasPS(false)}
              className="btn-secondary flex-1"
            >
              No - Generate suggestions
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Generate PS Options */}
      {hasPS === false && psOptions.length === 0 && (
        <div className="card space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">Generate Problem Statement</h2>
          <p className="text-gray-600">Provide a hint about your ML problem (optional)</p>
          <input
            type="text"
            className="input-field"
            placeholder="e.g., customer behavior, sales forecasting, fraud detection"
            value={formData.hint}
            onChange={(e) => setFormData({ ...formData, hint: e.target.value })}
          />
          <button
            type="button"
            onClick={handleGeneratePS}
            disabled={generatingPS}
            className="btn-primary flex items-center space-x-2"
          >
            {generatingPS ? (
              <>
                <Loader className="animate-spin" size={18} />
                <span>Generating...</span>
              </>
            ) : (
              <span>Generate Problem Statements</span>
            )}
          </button>
          <button
            type="button"
            onClick={() => setHasPS(null)}
            className="btn-secondary w-full"
          >
            Back
          </button>
        </div>
      )}

      {/* Step 3: Show Generated Options */}
      {psOptions.length > 0 && (
        <div className="card space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">Choose a Problem Statement</h2>
          <div className="space-y-3">
            {psOptions.map((option, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:border-primary-500 transition-colors">
                <h3 className="font-semibold text-gray-900 mb-2">Option {index + 1}</h3>
                <p className="text-gray-700 mb-3">{option.statement || option.raw_text}</p>
                <button
                  type="button"
                  onClick={() => handleSelectOption(option)}
                  className="btn-primary"
                >
                  Use This Statement
                </button>
              </div>
            ))}
          </div>
          <button
            type="button"
            onClick={() => { setPsOptions([]); setHasPS(null) }}
            className="btn-secondary w-full"
          >
            Back
          </button>
        </div>
      )}

      {/* Step 4: Main Form */}
      {(hasPS === true || formData.problemStatement) && psOptions.length === 0 && (
        <form onSubmit={handleSubmit} className="card space-y-6">
          {/* Problem Statement */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Problem Statement *
            </label>
            <textarea
              required
              rows={4}
              className="input-field"
              placeholder="Example: Predict customer churn based on usage patterns and demographics"
              value={formData.problemStatement}
              onChange={(e) => setFormData({ ...formData, problemStatement: e.target.value })}
            />
            <p className="mt-1 text-sm text-gray-500">
              Describe what you want to predict or classify
            </p>
          </div>
        
        {/* Training Budget */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Training Budget (minutes)
          </label>
          <input
            type="number"
            min="1"
            max="60"
            className="input-field"
            value={formData.trainingBudget}
            onChange={(e) => setFormData({ ...formData, trainingBudget: parseInt(e.target.value) })}
          />
          <p className="mt-1 text-sm text-gray-500">
            How long to spend training models (1-60 minutes)
          </p>
        </div>
        
        {/* Primary Metric */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Primary Metric
          </label>
          <select
            className="input-field"
            value={formData.primaryMetric}
            onChange={(e) => setFormData({ ...formData, primaryMetric: e.target.value })}
          >
            <option value="f1">F1 Score (Classification)</option>
            <option value="accuracy">Accuracy (Classification)</option>
            <option value="roc_auc">ROC AUC (Classification)</option>
            <option value="r2">R² Score (Regression)</option>
            <option value="mse">MSE (Regression)</option>
          </select>
          <p className="mt-1 text-sm text-gray-500">
            Metric to optimize during training
          </p>
        </div>
        
        {/* File Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Upload Dataset (Optional)
          </label>
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg cursor-pointer transition-colors">
              <Upload size={18} />
              <span className="text-sm">Choose File</span>
              <input
                type="file"
                accept=".csv,.xlsx,.xls"
                className="hidden"
                onChange={(e) => setFormData({ ...formData, file: e.target.files[0] })}
              />
            </label>
            {formData.file && (
              <span className="text-sm text-gray-600">{formData.file.name}</span>
            )}
          </div>
          <p className="mt-1 text-sm text-gray-500">
            Leave empty to auto-find datasets from Kaggle/HuggingFace
          </p>
        </div>
        
          {/* Submit Button */}
          <div className="flex justify-end space-x-4 pt-4">
            <button
              type="button"
              onClick={() => { setHasPS(null); setFormData({ ...formData, problemStatement: '' }) }}
              className="btn-secondary"
              disabled={loading}
            >
              Back
            </button>
            <button
              type="submit"
              className="btn-primary flex items-center space-x-2"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader className="animate-spin" size={18} />
                  <span>Starting...</span>
                </>
              ) : (
                <>
                  <Play size={18} />
                  <span>Start Run</span>
                </>
              )}
            </button>
          </div>
        </form>
      )}
      
      {/* Examples */}
      <div className="mt-8 card bg-blue-50 border border-blue-200">
        <h3 className="font-semibold text-gray-900 mb-3">Example Problem Statements:</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li>• "Predict house prices based on location, size, and amenities"</li>
          <li>• "Classify customer reviews as positive, negative, or neutral"</li>
          <li>• "Forecast sales for the next quarter based on historical data"</li>
          <li>• "Detect fraudulent transactions in credit card data"</li>
        </ul>
      </div>
    </div>
  )
}
