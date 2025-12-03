import { Link, useLocation } from 'react-router-dom'
import { Home, Play, List, Github } from 'lucide-react'

export default function Layout({ children }) {
  const location = useLocation()
  
  const isActive = (path) => location.pathname === path
  
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <Link to="/" className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">A</span>
                </div>
                <span className="text-xl font-bold text-gray-900">AutoML Platform</span>
              </Link>
              
              <nav className="hidden md:flex space-x-4">
                <Link
                  to="/"
                  className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium ${
                    isActive('/') 
                      ? 'bg-primary-50 text-primary-700' 
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Home size={18} />
                  <span>Home</span>
                </Link>
                
                <Link
                  to="/new-run"
                  className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium ${
                    isActive('/new-run') 
                      ? 'bg-primary-50 text-primary-700' 
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Play size={18} />
                  <span>New Run</span>
                </Link>
                
                <Link
                  to="/runs"
                  className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium ${
                    isActive('/runs') 
                      ? 'bg-primary-50 text-primary-700' 
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <List size={18} />
                  <span>All Runs</span>
                </Link>
              </nav>
            </div>
            
            <div className="flex items-center space-x-4">
              <a
                href="https://github.com/yourusername/automl-platform"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-gray-900"
              >
                <Github size={20} />
              </a>
            </div>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>
      
      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            © 2024 AutoML Platform. Built with React + FastAPI.
          </p>
        </div>
      </footer>
    </div>
  )
}
