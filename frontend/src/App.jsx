import { useState } from "react"
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom"
import Dashboard from "./pages/Dashboard"
import Violations from "./pages/Violations"
import Cameras from "./pages/Cameras"

export default function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-950 text-white">
        
        {/* Navbar */}
        <nav className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></div>
            <h1 className="text-lg font-bold text-white">Traffic Violation Detection</h1>
            <span className="text-xs text-gray-400 bg-gray-800 px-2 py-1 rounded">Bangalore</span>
          </div>
          <div className="flex gap-6">
            <Link to="/" className="text-sm text-gray-300 hover:text-white transition">Dashboard</Link>
            <Link to="/violations" className="text-sm text-gray-300 hover:text-white transition">Violations</Link>
            <Link to="/cameras" className="text-sm text-gray-300 hover:text-white transition">Cameras</Link>
          </div>
        </nav>

        {/* Pages */}
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/violations" element={<Violations />} />
          <Route path="/cameras" element={<Cameras />} />
        </Routes>

      </div>
    </Router>
  )
}