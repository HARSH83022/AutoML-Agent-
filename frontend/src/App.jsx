import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import NewRunPage from './pages/NewRunPage'
import RunDetailsPage from './pages/RunDetailsPage'
import RunsListPage from './pages/RunsListPage'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/new-run" element={<NewRunPage />} />
          <Route path="/runs" element={<RunsListPage />} />
          <Route path="/runs/:runId" element={<RunDetailsPage />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
