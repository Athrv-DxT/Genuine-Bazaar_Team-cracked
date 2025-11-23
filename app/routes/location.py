"""
Location-related routes (states, cities, current location)
"""
from fastapi import APIRouter
import json
from pathlib import Path

router = APIRouter(prefix="/location", tags=["location"])

# Load Indian states and cities
STATES_CITIES_FILE = Path(__file__).parent.parent / "data" / "indian_states_cities.json"

@router.get("/states")
async def get_states():
    """Get list of Indian states"""
    try:
        with open(STATES_CITIES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {
            "states": list(data.keys()),
            "count": len(data)
        }
    except Exception as e:
        # Fallback if file not found
        return {
            "states": [
                "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
                "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
                "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
                "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
                "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
                "Uttar Pradesh", "Uttarakhand", "West Bengal"
            ],
            "count": 28
        }

@router.get("/cities/{state}")
async def get_cities(state: str):
    """Get cities for a specific state"""
    try:
        with open(STATES_CITIES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        cities = data.get(state, [])
        return {
            "state": state,
            "cities": cities,
            "count": len(cities)
        }
    except Exception as e:
        return {
            "state": state,
            "cities": [],
            "count": 0,
            "error": str(e)
        }

