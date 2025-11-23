import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import './Keywords.css'

export default function Keywords() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [keyword, setKeyword] = useState('')
  const [category, setCategory] = useState('')

  const { data: keywords, isLoading } = useQuery({
    queryKey: ['keywords'],
    queryFn: async () => {
      const response = await axios.get('/keywords')
      return response.data
    }
  })

  const addKeywordMutation = useMutation({
    mutationFn: async (data) => {
      await axios.post('/keywords', data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['keywords'])
      setKeyword('')
      setCategory('')
    }
  })

  const deleteKeywordMutation = useMutation({
    mutationFn: async (keywordId) => {
      await axios.delete(`/keywords/${keywordId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['keywords'])
    }
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    addKeywordMutation.mutate({ keyword, category })
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
        <h1>Tracked Keywords</h1>
        <p>Add keywords to track for demand peaks and promotion opportunities</p>

        <form onSubmit={handleSubmit} className="keyword-form">
          <div className="form-row">
            <input
              type="text"
              placeholder="Keyword (e.g., umbrella, cold drink)"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              required
            />
            <input
              type="text"
              placeholder="Category (optional)"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            />
            <button type="submit" disabled={addKeywordMutation.isLoading}>
              {addKeywordMutation.isLoading ? 'Adding...' : 'Add Keyword'}
            </button>
          </div>
        </form>

        {isLoading ? (
          <div className="loading">Loading keywords...</div>
        ) : keywords && keywords.length > 0 ? (
          <div className="keywords-list">
            {keywords.map(kw => (
              <div key={kw.id} className="keyword-card">
                <div>
                  <h4>{kw.keyword}</h4>
                  {kw.category && <p className="category">{kw.category}</p>}
                </div>
                <button
                  onClick={() => deleteKeywordMutation.mutate(kw.id)}
                  className="delete-btn"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-keywords">
            <p>No keywords tracked yet. Add keywords to start receiving alerts.</p>
          </div>
        )}
      </div>
    </div>
  )
}


