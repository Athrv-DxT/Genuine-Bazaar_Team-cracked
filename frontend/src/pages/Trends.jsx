import React, { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import './Trends.css'

export default function Trends() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [searchKeyword, setSearchKeyword] = useState('')
  const [searchResults, setSearchResults] = useState(null)
  const [searching, setSearching] = useState(false)

  const { data: trendsData, isLoading, error: trendsError } = useQuery({
    queryKey: ['trends', 'my-industries'],
    queryFn: async () => {
      const response = await axios.get('/trends/my-industries')
      return response.data
    },
    enabled: !!user,
    retry: 2,
    refetchOnWindowFocus: false,
    staleTime: 5 * 60 * 1000
  })

  // Always ensure we have trends to display
  const displayTrends = useMemo(() => {
    if (trendsData?.trends && Object.keys(trendsData.trends).length > 0) {
      return trendsData.trends
    }
    
    // Fallback trends - always show something
    const defaultCategories = user?.market_categories || ['electronics', 'clothes', 'food']
    const fallbackTrends = {}
    
    defaultCategories.forEach(category => {
      const keywords = {
        'electronics': ['smartphone', 'laptop', 'headphones', 'tablet', 'smartwatch'],
        'clothes': ['t-shirt', 'jeans', 'dress', 'jacket', 'shoes'],
        'food': ['pizza', 'burger', 'coffee', 'snacks', 'ice cream'],
        'beauty': ['lipstick', 'skincare', 'perfume', 'makeup', 'shampoo'],
        'home': ['furniture', 'sofa', 'bed', 'lamp', 'decor'],
        'sports': ['cricket', 'football', 'fitness', 'yoga', 'gym']
      }[category] || ['product', 'item', 'popular', 'trending', 'new']
      
      fallbackTrends[category] = keywords.map((keyword, idx) => ({
        keyword,
        trend_score: 40 + (idx * 8) + (Math.random() * 20),
        status: idx < 2 ? 'trending' : 'rising',
        source: 'default'
      }))
    })
    
    return fallbackTrends
  }, [trendsData, user?.market_categories])

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchKeyword.trim()) return

    setSearching(true)
    setSearchResults(null)

    try {
      const response = await axios.get('/trends/search', {
        params: { keyword: searchKeyword.trim() }
      })
      setSearchResults(response.data)
    } catch (error) {
      if (error.response?.status === 404) {
        setSearchResults({
          keyword: searchKeyword.trim(),
          error: error.response?.data?.detail || 'No genuine trend data found. This keyword may not be trending or may not exist in news sources.',
          trend_score: 0,
          status: 'none',
          source: 'none'
        })
      } else if (error.response?.status === 400) {
        setSearchResults({
          keyword: searchKeyword.trim(),
          error: error.response?.data?.detail || 'Invalid keyword. Please enter at least 3 characters.',
          trend_score: 0,
          status: 'none',
          source: 'none'
        })
      } else {
        setSearchResults({
          keyword: searchKeyword.trim(),
          error: 'Error connecting to trend service. Please try again later.',
          trend_score: 0,
          status: 'none',
          source: 'none'
        })
      }
    } finally {
      setSearching(false)
    }
  }

  const emojiMap = {
    'clothes': '👔',
    'electronics': '📱',
    'food': '🍔',
    'beauty': '💄',
    'home': '🏠',
    'sports': '⚽',
    'books': '📚',
    'toys': '🧸',
    'automotive': '🚗',
    'other': '📦'
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
        <div className="trends-header">
          <div>
            <h1>Industry Trends</h1>
            <p>Real-time trends powered by GDELT for your market categories</p>
          </div>
          
          {/* Keyword Search */}
          <div className="keyword-search-section">
            <form onSubmit={handleSearch} className="keyword-search-form">
              <input
                type="text"
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                placeholder="Search keywords (e.g., headphones, t-shirt)"
                className="keyword-search-input"
                disabled={searching}
              />
              <button 
                type="submit" 
                className="keyword-search-button"
                disabled={searching || !searchKeyword.trim()}
              >
                {searching ? '⏳' : '🔍'}
              </button>
            </form>
            
            {searchResults && (
              <div className={`search-result-card ${searchResults.error ? 'error' : searchResults.status}`}>
                <div className="search-result-header">
                  <h3>{searchResults.keyword}</h3>
                  {!searchResults.error && (
                    <span className={`trend-badge ${searchResults.status}`}>
                      {searchResults.status}
                    </span>
                  )}
                </div>
                {searchResults.error ? (
                  <div>
                    <p className="search-error">❌ {searchResults.error}</p>
                    <p style={{ marginTop: '12px', fontSize: '13px', color: '#666' }}>
                      Try searching for real product keywords like: smartphone, laptop, headphones, t-shirt, jeans, etc.
                    </p>
                  </div>
                ) : (
                  <>
                    <div className="trend-score">
                      <div className="score-bar">
                        <div 
                          className="score-fill" 
                          style={{ width: `${searchResults.trend_score || 0}%` }}
                        ></div>
                      </div>
                      <span className="score-value">{Math.round(searchResults.trend_score || 0)}/100</span>
                    </div>
                    <p className="search-source">Source: {searchResults.source || 'GDELT'}</p>
                  </>
                )}
              </div>
            )}
          </div>
        </div>

        {isLoading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading trends from GDELT...</p>
          </div>
        ) : trendsError ? (
          <div className="error-message">
            <p>⚠️ Error loading trends: {trendsError.message}</p>
            <p style={{ marginTop: '8px', fontSize: '14px', color: '#666' }}>
              Showing default trends below...
            </p>
          </div>
        ) : null}

        {/* Always show trends - never empty */}
        {displayTrends && Object.keys(displayTrends).length > 0 && (
          <div className="trends-container">
            {Object.entries(displayTrends).map(([industry, trends]) => {
              if (!trends || trends.length === 0) return null
              
              return (
                <div key={industry} className="industry-trends">
                  <h2 className="industry-title">
                    <span style={{ fontSize: '32px', marginRight: '12px' }}>
                      {emojiMap[industry] || '📦'}
                    </span>
                    {industry.charAt(0).toUpperCase() + industry.slice(1)} Trends
                    <span style={{ marginLeft: '12px', fontSize: '16px', color: '#999', fontWeight: 'normal' }}>
                      ({trends.length} trending)
                    </span>
                  </h2>
                  <div className="trends-grid">
                    {trends.map((trend, index) => (
                      <div key={`${trend.keyword}-${index}`} className={`trend-card ${trend.status || 'rising'}`}>
                        <div className="trend-header">
                          <span className="trend-rank">#{index + 1}</span>
                          <span className={`trend-badge ${trend.status || 'rising'}`}>
                            {trend.status || 'rising'}
                          </span>
                        </div>
                        <h3>{trend.keyword}</h3>
                        <div className="trend-score">
                          <div className="score-bar">
                            <div 
                              className="score-fill" 
                              style={{ width: `${Math.min(100, Math.max(0, trend.trend_score || 0))}%` }}
                            ></div>
                          </div>
                          <span className="score-value">{Math.round(trend.trend_score || 0)}/100</span>
                        </div>
                        {trend.season && (
                          <p className="season-badge">🌤️ Season: {trend.season}</p>
                        )}
                        {trend.category && trend.category !== 'general' && (
                          <p className="category-badge">📁 {trend.category}</p>
                        )}
                        {trend.source && (
                          <p className="source-badge">📡 {trend.source}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
