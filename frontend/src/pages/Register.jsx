import React, { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import axios from 'axios'
import './Auth.css'

const MARKET_CATEGORIES = [
  'electronics',
  'clothes',
  'food',
  'beauty',
  'home',
  'sports',
  'books',
  'toys',
  'automotive',
  'other'
]

export default function Register() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    business_name: '',
    market_category: '',
    location_city: '',
    location_state: '',
    location_country: 'IN'
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [states, setStates] = useState([])
  const [cities, setCities] = useState([])
  const [loadingLocation, setLoadingLocation] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  // Load states on mount
  useEffect(() => {
    axios.get('/location/states')
      .then(response => {
        setStates(response.data.states || [])
      })
      .catch(err => {
        console.error('Error loading states:', err)
      })
  }, [])

  // Load cities when state changes
  useEffect(() => {
    if (formData.location_state) {
      axios.get(`/location/cities/${encodeURIComponent(formData.location_state)}`)
        .then(response => {
          setCities(response.data.cities || [])
        })
        .catch(err => {
          console.error('Error loading cities:', err)
          setCities([])
        })
    } else {
      setCities([])
    }
  }, [formData.location_state])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => {
      const newData = { ...prev, [name]: value }
      // Clear city if state changes
      if (name === 'location_state') {
        newData.location_city = ''
      }
      return newData
    })
  }

  const handleCategoryChange = (category) => {
    setFormData(prev => ({
      ...prev,
      market_category: category
    }))
  }

  const handleUseCurrentLocation = () => {
    setLoadingLocation(true)
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          try {
            // Reverse geocoding using a free service
            const { latitude, longitude } = position.coords
            const response = await fetch(
              `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${latitude}&longitude=${longitude}&localityLanguage=en`
            )
            const data = await response.json()
            
            if (data.locality && data.principalSubdivision) {
              setFormData(prev => ({
                ...prev,
                location_city: data.locality || '',
                location_state: data.principalSubdivision || ''
              }))
              
              // Load cities for the detected state
              if (data.principalSubdivision) {
                axios.get(`/location/cities/${encodeURIComponent(data.principalSubdivision)}`)
                  .then(response => {
                    setCities(response.data.cities || [])
                  })
                  .catch(err => console.error('Error loading cities:', err))
              }
            }
          } catch (err) {
            console.error('Error getting location:', err)
            alert('Could not detect location. Please select manually.')
          } finally {
            setLoadingLocation(false)
          }
        },
        (error) => {
          console.error('Geolocation error:', error)
          alert('Location access denied. Please select manually.')
          setLoadingLocation(false)
        }
      )
    } else {
      alert('Geolocation is not supported by your browser.')
      setLoadingLocation(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const registrationData = {
        ...formData,
        market_categories: formData.market_category ? [formData.market_category] : []
      }
      await register(registrationData)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card register-card">
        <div style={{ textAlign: 'center', marginBottom: '8px' }}>
          <div style={{ fontSize: '48px', marginBottom: '8px' }}>🚀</div>
          <h1>Create Account</h1>
        </div>
        <p className="subtitle">Join Genuine Bazaar - Your Trusted Retail Intelligence Platform</p>
        <form onSubmit={handleSubmit}>
          {error && <div className="error">{error}</div>}
          
          <div className="form-group">
            <label>Full Name</label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              required
              placeholder="Enter your full name"
            />
          </div>
          
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="your.email@example.com"
            />
          </div>
          
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Create a strong password"
              minLength={6}
            />
          </div>
          
          <div className="form-group">
            <label>Business Name (Optional)</label>
            <input
              type="text"
              name="business_name"
              value={formData.business_name}
              onChange={handleChange}
              placeholder="Your business/store name"
            />
          </div>
          
          <div className="form-group">
            <label>Market Category *</label>
            <div className="category-grid">
              {MARKET_CATEGORIES.map(cat => (
                <label key={cat} className="radio-label">
                  <input
                    type="radio"
                    name="market_category"
                    value={cat}
                    checked={formData.market_category === cat}
                    onChange={() => handleCategoryChange(cat)}
                    required
                  />
                  <span>{cat.charAt(0).toUpperCase() + cat.slice(1)}</span>
                </label>
              ))}
            </div>
          </div>
          
          <div className="form-group">
            <label>
              Location
              <button
                type="button"
                onClick={handleUseCurrentLocation}
                disabled={loadingLocation}
                style={{
                  marginLeft: '12px',
                  padding: '6px 12px',
                  fontSize: '12px',
                  background: 'transparent',
                  border: '1px solid #667eea',
                  borderRadius: '6px',
                  color: '#667eea',
                  cursor: 'pointer',
                  fontWeight: '500'
                }}
              >
                {loadingLocation ? 'Detecting...' : '📍 Use Current Location'}
              </button>
            </label>
            
            <div style={{ display: 'flex', gap: '12px', marginTop: '8px' }}>
              <select
                name="location_state"
                value={formData.location_state}
                onChange={handleChange}
                style={{
                  flex: 1,
                  padding: '14px 16px',
                  border: '2px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '16px',
                  background: 'white',
                  cursor: 'pointer'
                }}
              >
                <option value="">Select State</option>
                {states.map(state => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>
              
              <select
                name="location_city"
                value={formData.location_city}
                onChange={handleChange}
                disabled={!formData.location_state}
                style={{
                  flex: 1,
                  padding: '14px 16px',
                  border: '2px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '16px',
                  background: formData.location_state ? 'white' : '#f5f7fa',
                  cursor: formData.location_state ? 'pointer' : 'not-allowed',
                  opacity: formData.location_state ? 1 : 0.6
                }}
              >
                <option value="">Select City</option>
                {cities.map(city => (
                  <option key={city} value={city}>{city}</option>
                ))}
              </select>
            </div>
            {!formData.location_state && (
              <p style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                Select a state first to see cities
              </p>
            )}
          </div>
          
          <button type="submit" disabled={loading || loadingLocation}>
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
          
          <p className="auth-link">
            Already have an account? <Link to="/login">Login</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
