import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Alerts from './pages/Alerts'
import Keywords from './pages/Keywords'
import Trends from './pages/Trends'
import { AuthProvider, useAuth } from './context/AuthContext'
import './App.css'

function PrivateRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="loading">
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🛍️</div>
          <div>Loading Retail Cortex...</div>
        </div>
      </div>
    )
  }
  
  return user ? children : <Navigate to="/login" />
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/alerts"
        element={
          <PrivateRoute>
            <Alerts />
          </PrivateRoute>
        }
      />
      <Route
        path="/keywords"
        element={
          <PrivateRoute>
            <Keywords />
          </PrivateRoute>
        }
      />
      <Route
        path="/trends"
        element={
          <PrivateRoute>
            <Trends />
          </PrivateRoute>
        }
      />
      <Route path="/" element={<Navigate to="/dashboard" />} />
    </Routes>
  )
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  )
}

export default App


