from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from services.maps_service import MapsService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/nearby")
async def get_nearby_police_stations(lat: float, lon: float, radius: int = 5000):
    """Get nearby police stations based on location"""
    try:
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid coordinates"
            )
        
        # Validate radius
        if radius < 100 or radius > 50000:  # 100m to 50km
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Radius must be between 100 and 50000 meters"
            )
        
        # Get nearby police stations using Google Places API
        stations = await MapsService.find_nearby_police_stations(lat, lon, radius)
        
        if not stations:
            return {
                "stations": [],
                "total_count": 0,
                "message": "No police stations found in the specified area"
            }
        
        # Calculate distances and format response
        formatted_stations = []
        for station in stations:
            # Calculate distance (simplified - would use proper haversine formula in production)
            distance = MapsService.calculate_distance(
                lat, lon, 
                station["location"]["lat"], 
                station["location"]["lng"]
            )
            
            formatted_stations.append({
                "name": station["name"],
                "address": station.get("vicinity", "Address not available"),
                "phone": station.get("formatted_phone_number", None),
                "distance_meters": distance,
                "location": {
                    "lat": station["location"]["lat"],
                    "lon": station["location"]["lng"]
                },
                "rating": station.get("rating", None),
                "open_now": station.get("opening_hours", {}).get("open_now", None) if station.get("opening_hours") else None,
                "place_id": station.get("place_id")
            })
        
        # Sort by distance
        formatted_stations.sort(key=lambda x: x["distance_meters"])
        
        return {
            "stations": formatted_stations,
            "total_count": len(formatted_stations),
            "search_center": {"lat": lat, "lon": lon},
            "search_radius": radius
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding nearby police stations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find nearby police stations"
        )

@router.get("/helplines")
async def get_emergency_helplines():
    """Get list of national emergency helplines"""
    try:
        helplines = [
            {
                "name": "Police",
                "number": "100",
                "description": "For immediate police assistance",
                "available_24x7": True,
                "category": "emergency"
            },
            {
                "name": "Women Helpline",
                "number": "1091",
                "description": "24/7 women safety helpline",
                "available_24x7": True,
                "category": "women_safety"
            },
            {
                "name": "Domestic Abuse Helpline",
                "number": "181",
                "description": "Domestic violence and abuse helpline",
                "available_24x7": True,
                "category": "women_safety"
            },
            {
                "name": "Child Helpline",
                "number": "1098",
                "description": "Child protection and emergency services",
                "available_24x7": True,
                "category": "child_safety"
            },
            {
                "name": "Ambulance",
                "number": "108" if False else "102",  # 108 in some states, 102 in others
                "description": "Medical emergency services",
                "available_24x7": True,
                "category": "medical"
            },
            {
                "name": "Fire Brigade",
                "number": "101",
                "description": "Fire emergency services",
                "available_24x7": True,
                "category": "emergency"
            },
            {
                "name": "National Emergency Number",
                "number": "112",
                "description": "Single emergency number for all services",
                "available_24x7": True,
                "category": "emergency"
            },
            {
                "name": "Cyber Crime Helpline",
                "number": "1930",
                "description": "Report cyber crimes and online fraud",
                "available_24x7": True,
                "category": "cyber_crime"
            },
            {
                "name": "Anti-Ragging Helpline",
                "number": "1800-180-5522",
                "description": "Report ragging in educational institutions",
                "available_24x7": False,
                "available_hours": "9:00 AM - 6:00 PM",
                "category": "education"
            },
            {
                "name": "Mental Health Helpline",
                "number": "1860-266-2345",
                "description": "Mental health support and counseling",
                "available_24x7": False,
                "available_hours": "24/7 (Toll-free)",
                "category": "mental_health"
            }
        ]
        
        return {
            "helplines": helplines,
            "total_count": len(helplines),
            "last_updated": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error fetching emergency helplines: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch emergency helplines"
        )

@router.get("/station/{place_id}")
async def get_police_station_details(place_id: str):
    """Get detailed information about a specific police station"""
    try:
        # Get detailed place information from Google Places API
        station_details = await MapsService.get_place_details(place_id)
        
        if not station_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Police station not found"
            )
        
        # Format response
        response = {
            "name": station_details.get("name"),
            "address": station_details.get("formatted_address"),
            "phone": station_details.get("formatted_phone_number"),
            "location": {
                "lat": station_details["geometry"]["location"]["lat"],
                "lon": station_details["geometry"]["location"]["lng"]
            },
            "rating": station_details.get("rating"),
            "user_ratings_total": station_details.get("user_ratings_total"),
            "website": station_details.get("website"),
            "opening_hours": station_details.get("opening_hours"),
            "photos": [photo.get("photo_reference") for photo in station_details.get("photos", [])[:5]],
            "reviews": station_details.get("reviews", [])[:3],  # Get first 3 reviews
            "place_id": station_details.get("place_id")
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching police station details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch police station details"
        )

@router.get("/directions")
async def get_directions_to_police(lat: float, lon: float, destination_lat: float, destination_lon: float):
    """Get directions from current location to police station"""
    try:
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid current coordinates"
            )
        
        if not (-90 <= destination_lat <= 90) or not (-180 <= destination_lon <= 180):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid destination coordinates"
            )
        
        # Get directions using Google Maps Directions API
        directions = await MapsService.get_directions(lat, lon, destination_lat, destination_lon)
        
        if not directions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not find directions to the specified location"
            )
        
        return {
            "directions": directions,
            "origin": {"lat": lat, "lon": lon},
            "destination": {"lat": destination_lat, "lon": destination_lon}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting directions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get directions"
        )
