import { Link } from 'react-router-dom'
import { Play, Database, Brain, Rocket, CheckCircle } from 'lucide-react'

export default function HomePage() {
  const features = [
    {
      icon: <Database className="w-6 h-6" />,
      title: 'Auto Data Collection',
      description: 'Automatically finds datasets from Kaggle, HuggingFace, and UCI'
    },
    {
      icon: <Brain className="w-6 h-6" />,
      title: 'Smart ML Training',
      description: 'Trains multiple models and picks the best one automatically'
    },
    {
      icon: <Rocket className="w-6 h-6" />,
      title: 'One-Click Deploy',
      description: 'Generate deployment configs for Docker, FastAPI, and more'
    },
    {
      icon: <CheckCircle className="w-6 h-6" />,
      title: 'No Code Required',
      description: 'Just describe your problem in plain English'
    },
  ]
  
  return (
    <div className="bg-gradient-to-b from-primary-50 to-white">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Build ML Models
            <span className="block text-primary-600">Without Writing Code</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Describe your machine learning problem in plain English. 
            Our AI agents handle data collection, training, and deployment automatically.
          </p>
          <div className="flex justify-center space-x-4">
            <Link to="/new-run" className="btn-primary flex items-center space-x-2 text-lg px-8 py-3">
              <Play size={20} />
              <span>Start New Run</span>
            </Link>
            <Link to="/runs" className="btn-secondary text-lg px-8 py-3">
              View Past Runs
            </Link>
          </div>
        </div>
      </div>
      
      {/* Features Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          How It Works
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="card text-center hover:shadow-lg transition-shadow">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-100 text-primary-600 rounded-lg mb-4">
                {feature.icon}
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600 text-sm">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
      
      {/* Stats Section */}
      <div className="bg-primary-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold mb-2">10+</div>
              <div className="text-primary-100">ML Algorithms</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">3</div>
              <div className="text-primary-100">Data Sources</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">100%</div>
              <div className="text-primary-100">Automated</div>
            </div>
          </div>
        </div>
      </div>
      
      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Ready to Build Your First Model?
        </h2>
        <p className="text-xl text-gray-600 mb-8">
          It takes less than 5 minutes to get started
        </p>
        <Link to="/new-run" className="btn-primary text-lg px-8 py-3 inline-flex items-center space-x-2">
          <Play size={20} />
          <span>Get Started Now</span>
        </Link>
      </div>
    </div>
  )
}
