from plyer import gps
from kivy.clock import Clock
from kivy.logger import Logger
import time
from typing import Optional, Dict, Any
from config import GPS_ACCURACY_THRESHOLD, LOCATION_UPDATE_INTERVAL

class LocationService:
    """GPS location service for real-time location tracking"""
    
    def __init__(self):
        self.gps = gps
        self.current_location = None
        self.last_update_time = 0
        self.is_tracking = False
        self.callbacks = []
        
    def initialize(self):
        """Initialize GPS service"""
        try:
            # Configure GPS
            self.gps.configure(
                on_location=self.on_location,
                on_status=self.on_status
            )
            
            # Start GPS
            self.gps.start()
            self.is_tracking = True
            
            Logger.info("LocationService: GPS initialized and started")
            
        except Exception as e:
            Logger.error(f"LocationService: Error initializing GPS: {e}")
    
    def on_location(self, **kwargs):
        """Callback for GPS location updates"""
        try:
            lat = kwargs.get('lat')
            lon = kwargs.get('lon')
            accuracy = kwargs.get('accuracy')
            
            if lat and lon:
                # Check accuracy threshold
                if accuracy and accuracy > GPS_ACCURACY_THRESHOLD:
                    Logger.warning(f"LocationService: Low accuracy location: {accuracy}m")
                    return
                
                # Update current location
                self.current_location = {
                    'lat': lat,
                    'lon': lon,
                    'accuracy': accuracy,
                    'timestamp': time.time(),
                    'speed': kwargs.get('speed', 0),
                    'altitude': kwargs.get('altitude', 0),
                    'bearing': kwargs.get('bearing', 0)
                }
                
                self.last_update_time = time.time()
                
                # Notify callbacks
                for callback in self.callbacks:
                    try:
                        callback(self.current_location)
                    except Exception as e:
                        Logger.error(f"LocationService: Error in callback: {e}")
                
                Logger.info(f"LocationService: Location updated: {lat:.6f}, {lon:.6f}")
                
        except Exception as e:
            Logger.error(f"LocationService: Error processing location: {e}")
    
    def on_status(self, stype, status):
        """Callback for GPS status updates"""
        try:
            Logger.info(f"LocationService: GPS Status - {stype}: {status}")
            
            if stype == 'provider-enabled':
                Logger.info("LocationService: GPS provider enabled")
            elif stype == 'provider-disabled':
                Logger.warning("LocationService: GPS provider disabled")
            elif stype == 'gps-started':
                Logger.info("LocationService: GPS started")
            elif stype == 'gps-stopped':
                Logger.warning("LocationService: GPS stopped")
                
        except Exception as e:
            Logger.error(f"LocationService: Error processing status: {e}")
    
    def get_current_location(self) -> Optional[Dict[str, Any]]:
        """Get current location"""
        # Check if location is recent (within last 5 minutes)
        if self.current_location:
            age = time.time() - self.current_location.get('timestamp', 0)
            if age < 300:  # 5 minutes
                return self.current_location
        
        return None
    
    def start_tracking(self):
        """Start GPS tracking"""
        try:
            if not self.is_tracking:
                self.gps.start()
                self.is_tracking = True
                Logger.info("LocationService: GPS tracking started")
        except Exception as e:
            Logger.error(f"LocationService: Error starting GPS: {e}")
    
    def stop_tracking(self):
        """Stop GPS tracking"""
        try:
            if self.is_tracking:
                self.gps.stop()
                self.is_tracking = False
                Logger.info("LocationService: GPS tracking stopped")
        except Exception as e:
            Logger.error(f"LocationService: Error stopping GPS: {e}")
    
    def add_location_callback(self, callback):
        """Add callback for location updates"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def remove_location_callback(self, callback):
        """Remove location callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def get_location_age(self) -> float:
        """Get age of current location in seconds"""
        if self.current_location:
            return time.time() - self.current_location.get('timestamp', 0)
        return float('inf')
    
    def is_location_fresh(self, max_age: int = LOCATION_UPDATE_INTERVAL) -> bool:
        """Check if location is fresh"""
        return self.get_location_age() < max_age
    
    def get_distance_from(self, lat: float, lon: float) -> float:
        """Calculate distance from current location to given coordinates"""
        if not self.current_location:
            return float('inf')
        
        try:
            from geopy.distance import geodesic
            
            current_coords = (self.current_location['lat'], self.current_location['lon'])
            target_coords = (lat, lon)
            
            distance = geodesic(current_coords, target_coords).meters
            return distance
            
        except Exception as e:
            Logger.error(f"LocationService: Error calculating distance: {e}")
            return float('inf')
    
    def is_within_radius(self, lat: float, lon: float, radius: float) -> bool:
        """Check if current location is within radius of target"""
        distance = self.get_distance_from(lat, lon)
        return distance <= radius
    
    def format_location_text(self) -> str:
        """Format current location as text"""
        if not self.current_location:
            return "Location not available"
        
        lat = self.current_location['lat']
        lon = self.current_location['lon']
        accuracy = self.current_location.get('accuracy', 0)
        
        text = f"{lat:.6f}, {lon:.6f}"
        if accuracy:
            text += f" (±{accuracy:.0f}m)"
        
        return text
    
    def get_gps_status(self) -> Dict[str, Any]:
        """Get GPS status information"""
        return {
            'is_tracking': self.is_tracking,
            'has_location': self.current_location is not None,
            'location_age': self.get_location_age(),
            'is_fresh': self.is_location_fresh(),
            'last_update': self.last_update_time
        }
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.stop_tracking()
            self.callbacks.clear()
            Logger.info("LocationService: Cleanup completed")
        except Exception as e:
            Logger.error(f"LocationService: Error during cleanup: {e}")
