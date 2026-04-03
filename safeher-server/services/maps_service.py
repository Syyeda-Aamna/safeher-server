import requests
import math
from typing import List, Dict, Any, Optional
from config import settings
import logging

logger = logging.getLogger(__name__)

class MapsService:
    """Google Maps API integration service"""
    
    @staticmethod
    async def find_nearby_police_stations(lat: float, lon: float, radius: int = 5000) -> List[Dict[str, Any]]:
        """Find nearby police stations using Google Places API"""
        try:
            url = settings.GOOGLE_MAPS_PLACES_URL
            params = {
                "location": f"{lat},{lon}",
                "radius": radius,
                "type": "police",
                "key": settings.GOOGLE_MAPS_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "OK":
                logger.warning(f"Places API error: {data.get('status')} - {data.get('error_message', '')}")
                return []
            
            return data.get("results", [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch nearby police stations: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in find_nearby_police_stations: {str(e)}")
            return []
    
    @staticmethod
    async def get_place_details(place_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a place using Google Places API"""
        try:
            url = "https://maps.googleapis.com/maps/api/place/details/json"
            params = {
                "place_id": place_id,
                "fields": "name,formatted_address,formatted_phone_number,geometry,rating,user_ratings_total,website,opening_hours,photos,reviews",
                "key": settings.GOOGLE_MAPS_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "OK":
                logger.warning(f"Place Details API error: {data.get('status')} - {data.get('error_message', '')}")
                return None
            
            return data.get("result")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch place details: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_place_details: {str(e)}")
            return None
    
    @staticmethod
    async def geocode_address(address: str) -> Optional[Dict[str, Any]]:
        """Convert address to coordinates using Google Geocoding API"""
        try:
            url = settings.GOOGLE_MAPS_GEOCODE_URL
            params = {
                "address": address,
                "key": settings.GOOGLE_MAPS_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "OK":
                logger.warning(f"Geocoding API error: {data.get('status')} - {data.get('error_message', '')}")
                return None
            
            results = data.get("results", [])
            if not results:
                return None
            
            return results[0]  # Return first result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to geocode address: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in geocode_address: {str(e)}")
            return None
    
    @staticmethod
    async def reverse_geocode(lat: float, lon: float) -> Optional[str]:
        """Convert coordinates to address using Google Geocoding API"""
        try:
            url = settings.GOOGLE_MAPS_GEOCODE_URL
            params = {
                "latlng": f"{lat},{lon}",
                "key": settings.GOOGLE_MAPS_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "OK":
                logger.warning(f"Reverse geocoding API error: {data.get('status')} - {data.get('error_message', '')}")
                return None
            
            results = data.get("results", [])
            if not results:
                return None
            
            return results[0].get("formatted_address")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to reverse geocode coordinates: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in reverse_geocode: {str(e)}")
            return None
    
    @staticmethod
    async def get_directions(origin_lat: float, origin_lon: float, 
                           dest_lat: float, dest_lon: float, 
                           mode: str = "driving") -> Optional[Dict[str, Any]]:
        """Get directions between two points using Google Directions API"""
        try:
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                "origin": f"{origin_lat},{origin_lon}",
                "destination": f"{dest_lat},{dest_lon}",
                "mode": mode,
                "key": settings.GOOGLE_MAPS_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "OK":
                logger.warning(f"Directions API error: {data.get('status')} - {data.get('error_message', '')}")
                return None
            
            routes = data.get("routes", [])
            if not routes:
                return None
            
            # Format the response
            route = routes[0]
            leg = route["legs"][0]
            
            return {
                "distance": leg["distance"]["text"],
                "distance_meters": leg["distance"]["value"],
                "duration": leg["duration"]["text"],
                "duration_seconds": leg["duration"]["value"],
                "steps": [
                    {
                        "instruction": step["html_instructions"].replace("<b>", "").replace("</b>", ""),
                        "distance": step["distance"]["text"],
                        "duration": step["duration"]["text"]
                    }
                    for step in leg["steps"]
                ],
                "polyline": route.get("overview_polyline", {}).get("points")
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get directions: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_directions: {str(e)}")
            return None
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        try:
            # Convert latitude and longitude from degrees to radians
            lat1_rad = math.radians(lat1)
            lon1_rad = math.radians(lon1)
            lat2_rad = math.radians(lat2)
            lon2_rad = math.radians(lon2)
            
            # Haversine formula
            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad
            
            a = (math.sin(dlat/2)**2 + 
                 math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
            c = 2 * math.asin(math.sqrt(a))
            
            # Earth's radius in meters
            earth_radius = 6371000
            
            distance = earth_radius * c
            return round(distance, 2)
            
        except Exception as e:
            logger.error(f"Error calculating distance: {str(e)}")
            return 0
    
    @staticmethod
    async def get_static_map_url(lat: float, lon: float, zoom: int = 15, 
                               width: int = 600, height: int = 400,
                               markers: Optional[List[Dict]] = None) -> str:
        """Generate Google Static Map URL"""
        try:
            base_url = "https://maps.googleapis.com/maps/api/staticmap"
            params = {
                "center": f"{lat},{lon}",
                "zoom": zoom,
                "size": f"{width}x{height}",
                "maptype": "roadmap",
                "key": settings.GOOGLE_MAPS_KEY
            }
            
            # Add markers if provided
            if markers:
                marker_strings = []
                for marker in markers:
                    color = marker.get("color", "red")
                    label = marker.get("label", "")
                    marker_lat = marker.get("lat", lat)
                    marker_lon = marker.get("lon", lon)
                    
                    marker_str = f"color:{color}"
                    if label:
                        marker_str += f"|label:{label}"
                    marker_str += f"|{marker_lat},{marker_lon}"
                    marker_strings.append(marker_str)
                
                params["markers"] = "|".join(marker_strings)
            else:
                # Add default marker
                params["markers"] = f"color:red|{lat},{lon}"
            
            # Build URL
            param_string = "&".join([f"{k}={v}" for k, v in params.items()])
            return f"{base_url}?{param_string}"
            
        except Exception as e:
            logger.error(f"Error generating static map URL: {str(e)}")
            return ""
    
    @staticmethod
    async def validate_coordinates(lat: float, lon: float) -> bool:
        """Validate if coordinates are within valid ranges"""
        try:
            return (-90 <= lat <= 90) and (-180 <= lon <= 180)
        except Exception:
            return False
    
    @staticmethod
    async def get_nearby_hospitals(lat: float, lon: float, radius: int = 5000) -> List[Dict[str, Any]]:
        """Find nearby hospitals using Google Places API"""
        try:
            url = settings.GOOGLE_MAPS_PLACES_URL
            params = {
                "location": f"{lat},{lon}",
                "radius": radius,
                "type": "hospital",
                "key": settings.GOOGLE_MAPS_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "OK":
                logger.warning(f"Places API error for hospitals: {data.get('status')} - {data.get('error_message', '')}")
                return []
            
            return data.get("results", [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch nearby hospitals: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in find_nearby_hospitals: {str(e)}")
            return []
