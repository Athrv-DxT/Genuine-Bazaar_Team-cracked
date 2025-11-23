import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import './Alerts.css'

export default function Alerts() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [statusFilter, setStatusFilter] = useState('all')

  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts', statusFilter],
    queryFn: async () => {
      const params = statusFilter !== 'all' ? { status: statusFilter } : {}
      const response = await axios.get('/alerts', { params })
      return response.data
    }
  })

  const updateAlertMutation = useMutation({
    mutationFn: async ({ alertId, status }) => {
      await axios.patch(`/alerts/${alertId}`, { status })
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['alerts'])
    }
  })

  const handleStatusChange = (alertId, newStatus) => {
    updateAlertMutation.mutate({ alertId, status: newStatus })
  }

  return (
    <div className="dashboard">
      <nav className="navbar">
        <div className="nav-content">
          <h2>Retail Cortex</h2>
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
        <div className="page-header">
          <h1>Alerts</h1>
          <div className="filter-buttons">
            <button
              className={statusFilter === 'all' ? 'active' : ''}
              onClick={() => setStatusFilter('all')}
            >
              All
            </button>
            <button
              className={statusFilter === 'new' ? 'active' : ''}
              onClick={() => setStatusFilter('new')}
            >
              New
            </button>
            <button
              className={statusFilter === 'read' ? 'active' : ''}
              onClick={() => setStatusFilter('read')}
            >
              Read
            </button>
          </div>
        </div>

        {isLoading ? (
          <div className="loading">Loading alerts...</div>
        ) : alerts && alerts.length > 0 ? (
          <div className="alerts-list">
            {alerts.map(alert => (
              <div key={alert.id} className={`alert-card ${alert.priority}`}>
                <div className="alert-header">
                  <div>
                    <span className="alert-type">{alert.alert_type}</span>
                    <span className={`priority-badge ${alert.priority}`}>
                      {alert.priority}
                    </span>
                  </div>
                  <div className="alert-actions">
                    {alert.status === 'new' && (
                      <>
                        <button
                          onClick={() => handleStatusChange(alert.id, 'read')}
                          className="action-btn read"
                        >
                          Mark Read
                        </button>
                        <button
                          onClick={() => handleStatusChange(alert.id, 'acted')}
                          className="action-btn acted"
                        >
                          Mark Acted
                        </button>
                      </>
                    )}
                  </div>
                </div>
                <h4>{alert.title}</h4>
                <p>{alert.message}</p>
                {alert.keyword && (
                  <p className="keyword">Keyword: {alert.keyword}</p>
                )}
                {alert.predicted_impact && (
                  <p className="impact">
                    Predicted Impact: ₹{alert.predicted_impact.toFixed(0)}K
                  </p>
                )}
                {alert.context_data && Object.keys(alert.context_data).length > 0 && (
                  <div className="context-data">
                    <strong>Context:</strong>
                    <pre>{JSON.stringify(alert.context_data, null, 2)}</pre>
                  </div>
                )}
                <p className="timestamp">
                  {new Date(alert.created_at).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-alerts">
            <p>No alerts found.</p>
          </div>
        )}
      </div>
    </div>
  )
}


