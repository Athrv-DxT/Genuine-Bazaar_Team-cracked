# Retail Cortex 🚀

AI-powered retail intelligence platform that detects hidden demand peaks and identifies optimal promotion timing windows for retailers.

**Repository**: [https://github.com/Athrv-DxT/Genuine-Bazaar_Team-cracked](https://github.com/Athrv-DxT/Genuine-Bazaar_Team-cracked)

**Live Demo**: Deploy on [Render](https://render.com) using the included `render.yaml` configuration.

## Features

### 🎯 Demand Peak Detection
- **Weather-based opportunities**: Rain alerts, temperature spikes
- **Event-driven demand**: Local events causing micro-spikes
- **Social media trends**: Real-time trend detection
- **Competitor stockouts**: Opportunity windows when competitors are out of stock
- **Festival boosts**: Sub-category demand spikes during festivals

### 💰 Promotion Timing Engine
- **Sentiment peaks**: Launch promotions when trust/interest is rising
- **Festival priming days**: Optimal 3-7 day windows before festivals
- **High footfall hours**: Peak shopping time detection
- **Competitor inactivity**: Windows with less competition

### 🔐 User Management
- User authentication with JWT
- Market category selection (electronics, clothes, food, etc.)
- Location-based tracking
- Personalized alerts per retailer

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Production database (SQLite for local dev)
- **SQLAlchemy**: ORM
- **JWT**: Authentication
- **APScheduler**: Background job scheduling

### Frontend
- **React 18**: UI framework
- **React Router**: Navigation
- **TanStack Query**: Data fetching
- **Vite**: Build tool

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (for production)

### Backend Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (create `.env` file):
```env
DATABASE_URL=postgresql://user:password@localhost/retail_cortex
SECRET_KEY=your-secret-key-here
OPENWEATHER_API_KEY=your-openweather-api-key
CALENDARIFIC_API_KEY=your-calendarific-api-key
DEBUG=False
```

3. Initialize database:
```bash
python init_db.py
```

4. Run the server:
```bash
python -m uvicorn app.main:app --reload
```

Or with gunicorn for production:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create `.env` file:
```env
VITE_API_URL=http://localhost:8000/api
```

3. Run development server:
```bash
npm run dev
```

## Deployment on Render

### 1. Database Setup
- Create a PostgreSQL database on Render
- Note the internal database URL

### 2. Backend Deployment
- Connect your GitHub repository
- Set build command: `pip install -r requirements.txt`
- Set start command: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT app.main:app`
- Add environment variables:
  - `DATABASE_URL`: Your PostgreSQL connection string
  - `SECRET_KEY`: Generate a secure secret key
  - `OPENWEATHER_API_KEY`: Your OpenWeatherMap API key
  - `CALENDARIFIC_API_KEY`: Your Calendarific API key
  - `DEBUG`: `False`

### 3. Frontend Deployment
- Create a new static site on Render
- Build command: `cd frontend && npm install && npm run build`
- Publish directory: `frontend/dist`
- Add environment variable:
  - `VITE_API_URL`: Your backend API URL

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Alerts
- `GET /api/alerts` - Get all alerts
- `GET /api/alerts/new` - Get new alerts
- `POST /api/alerts/generate` - Manually generate alerts
- `PATCH /api/alerts/{id}` - Update alert status
- `DELETE /api/alerts/{id}` - Delete alert

### Keywords
- `GET /api/keywords` - Get tracked keywords
- `POST /api/keywords` - Add keyword
- `DELETE /api/keywords/{id}` - Delete keyword

## Getting API Keys

### OpenWeatherMap
1. Sign up at https://openweathermap.org/api
2. Get your free API key
3. Add to environment variables

### Calendarific
1. Sign up at https://calendarific.com/
2. Get your free API key
3. Add to environment variables

## Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   ├── auth.py              # Authentication utilities
│   ├── models/              # Database models
│   │   ├── user.py
│   │   └── alert.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── auth.py
│   │   └── alert.py
│   ├── routes/              # API routes
│   │   ├── auth.py
│   │   ├── alerts.py
│   │   └── keywords.py
│   ├── services/            # Business logic
│   │   ├── demand_detector.py
│   │   ├── promotion_timing.py
│   │   ├── weather_service.py
│   │   ├── holiday_service.py
│   │   └── trends_service.py
│   ├── jobs/                # Background jobs
│   │   └── alert_generator.py
│   └── scheduler.py         # Job scheduler
├── frontend/                # React frontend
│   ├── src/
│   │   ├── pages/
│   │   ├── context/
│   │   └── App.jsx
│   └── package.json
├── requirements.txt
├── render.yaml
├── Procfile
└── README.md
```

## License

[Your License Here]

## Support

For issues or questions, please open an issue in the repository.
