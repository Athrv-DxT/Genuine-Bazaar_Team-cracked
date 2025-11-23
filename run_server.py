"""
Simple script to run the Genuine Bazaar server
"""
import os
import sys
import subprocess

def check_env():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("[WARNING] No .env file found. Creating one with defaults...")
        with open('.env', 'w') as f:
            f.write("""# Database
DATABASE_URL=sqlite:///./genuine_bazaar.db

# Security
SECRET_KEY=dev-secret-key-change-in-production

# External API Keys (optional for basic testing)
OPENWEATHER_API_KEY=
CALENDARIFIC_API_KEY=

# App Settings
DEBUG=True
LOG_LEVEL=INFO
""")
        print("[OK] Created .env file. You can edit it to add API keys.")
        print()

def init_database():
    """Initialize database if needed"""
    print("Initializing database...")
    try:
        from app.database import engine, Base
        from app.models import User, Alert, TrackedKeyword, DemandSignal
        
        Base.metadata.create_all(bind=engine)
        print("[OK] Database initialized")
        return True
    except Exception as e:
        print(f"[FAIL] Database initialization failed: {e}")
        return False

def main():
    print("=" * 60)
    print("Genuine Bazaar - Starting Server")
    print("=" * 60)
    print()
    
    # Check .env
    check_env()
    
    # Initialize database
    if not init_database():
        print("\n[ERROR] Failed to initialize database. Exiting.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Starting server on http://localhost:8000")
    print("API docs available at http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    # Run uvicorn
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except Exception as e:
        print(f"\n[ERROR] Error starting server: {e}")
        print("\nTry installing dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()

