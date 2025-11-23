import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import './Dashboard.css'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts', 'new'],
    queryFn: async () => {
      const response = await axios.get('/alerts/new')
      return response.data
    }
  })

  const handleGenerateAlerts = async () => {
    try {
      await axios.post('/alerts/generate')
      window.location.reload()
    } catch (error) {
      alert('Error generating alerts')
    }
  }

  return (
    <div className="dashboard">
      <nav className="navbar">
        <div className="nav-content">
          <h2>Genuine Bazaar</h2>
          <div className="nav-links">
            <button onClick={() => navigate('/dashboard')}>Dashboard</button>
            <button onClick={() => navigate('/alerts')}>Alerts</button>
            <button onClick={() => navigate('/keywords')}>Keywords</button>
            <button onClick={() => navigate('/trends')}>Trends</button>
            <button onClick={logout}>Logout</button>
          </div>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="welcome-section">
          <h1>Welcome back, {user?.full_name}! 👋</h1>
          <p>Your AI-powered retail intelligence dashboard - Stay ahead of trends and maximize your sales</p>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <h3>New Alerts</h3>
            <p className="stat-number">{alerts?.length || 0}</p>
          </div>
          <div className="stat-card">
            <h3>Market Categories</h3>
            <p className="stat-number">{user?.market_categories?.length || 0}</p>
          </div>
          <div className="stat-card">
            <h3>Location</h3>
            <p className="stat-text">{user?.location_city || 'Not set'}</p>
          </div>
        </div>

        <div className="actions-section">
          <button className="primary-button" onClick={handleGenerateAlerts}>
            Generate New Alerts
          </button>
          <button className="secondary-button" onClick={() => navigate('/alerts')}>
            View All Alerts
          </button>
        </div>

        {isLoading ? (
          <div className="loading">Loading alerts...</div>
        ) : alerts && alerts.length > 0 ? (
          <div className="recent-alerts">
            <h2>Recent Alerts</h2>
            <div className="alerts-list">
              {alerts.slice(0, 5).map(alert => (
                <div key={alert.id} className={`alert-card ${alert.priority}`}>
                  <div className="alert-header">
                    <span className="alert-type">{alert.alert_type}</span>
                    <span className={`priority-badge ${alert.priority}`}>
                      {alert.priority}
                    </span>
                  </div>
                  <h4>{alert.title}</h4>
                  <p>{alert.message}</p>
                  {alert.predicted_impact && (
                    <p className="impact">
                      Predicted Impact: ₹{alert.predicted_impact.toFixed(0)}K
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="no-alerts">
            <p>No new alerts. Click "Generate New Alerts" to check for opportunities.</p>
          </div>
        )}
      </div>
    </div>
  )
}


