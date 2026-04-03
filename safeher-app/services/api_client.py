import requests
import json
from datetime import datetime
from config import API_BASE_URL, ENDPOINTS, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY

class APIClient:
    """API client for communicating with SafeHer server"""
    
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token = None
        self.session = requests.Session()
        self.session.timeout = REQUEST_TIMEOUT
        
    def set_token(self, token):
        """Set JWT token for authentication"""
        self.token = token
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            })
        else:
            self.session.headers.pop('Authorization', None)
            self.session.headers.pop('Content-Type', None)
    
    def _make_request(self, method, endpoint, data=None, params=None, require_auth=True):
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        # Check authentication requirement
        if require_auth and not self.token:
            return {'success': False, 'message': 'Authentication required'}
        
        # Retry logic
        for attempt in range(MAX_RETRIES):
            try:
                if method == 'GET':
                    response = self.session.get(url, params=params)
                elif method == 'POST':
                    response = self.session.post(url, json=data)
                elif method == 'PUT':
                    response = self.session.put(url, json=data)
                elif method == 'DELETE':
                    response = self.session.delete(url)
                else:
                    return {'success': False, 'message': 'Invalid HTTP method'}
                
                # Handle response
                if response.status_code == 200:
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        return {'success': True, 'data': response.text}
                
                elif response.status_code == 201:
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        return {'success': True, 'data': response.text}
                
                elif response.status_code == 401:
                    # Token expired or invalid
                    self.set_token(None)
                    return {'success': False, 'message': 'Authentication required', 'code': 'AUTH_REQUIRED'}
                
                elif response.status_code == 400:
                    try:
                        error_data = response.json()
                        return {'success': False, 'message': error_data.get('detail', 'Bad request')}
                    except json.JSONDecodeError:
                        return {'success': False, 'message': 'Bad request'}
                
                elif response.status_code == 404:
                    return {'success': False, 'message': 'Resource not found'}
                
                elif response.status_code == 500:
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                        continue
                    return {'success': False, 'message': 'Server error'}
                
                else:
                    return {'success': False, 'message': f'HTTP {response.status_code}'}
                    
            except requests.exceptions.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return {'success': False, 'message': 'Network error'}
        
        return {'success': False, 'message': 'Request failed after retries'}
    
    # Authentication endpoints
    def register_user(self, user_data):
        """Register a new user"""
        endpoint = ENDPOINTS['auth']['register']
        return self._make_request('POST', endpoint, data=user_data, require_auth=False)
    
    def verify_otp(self, phone, otp, purpose='register'):
        """Verify OTP"""
        endpoint = ENDPOINTS['auth']['verify_otp']
        data = {'phone': phone, 'otp': otp, 'purpose': purpose}
        return self._make_request('POST', endpoint, data=data, require_auth=False)
    
    def login(self, phone_or_email, password):
        """Login user"""
        endpoint = ENDPOINTS['auth']['login']
        # Determine if phone or email
        if '@' in phone_or_email:
            data = {'email': phone_or_email, 'password': password}
        else:
            data = {'phone': phone_or_email, 'password': password}
        return self._make_request('POST', endpoint, data=data, require_auth=False)
    
    def request_otp(self, phone, purpose='reset'):
        """Request OTP for password reset"""
        endpoint = ENDPOINTS['auth']['request_otp']
        data = {'phone': phone, 'purpose': purpose}
        return self._make_request('POST', endpoint, data=data, require_auth=False)
    
    def reset_password(self, phone, otp, new_password):
        """Reset password"""
        endpoint = ENDPOINTS['auth']['reset_password']
        data = {'phone': phone, 'otp': otp, 'new_password': new_password}
        return self._make_request('POST', endpoint, data=data, require_auth=False)
    
    def get_user_profile(self):
        """Get current user profile"""
        endpoint = ENDPOINTS['auth']['me']
        return self._make_request('GET', endpoint)
    
    # Contacts endpoints
    def get_contacts(self):
        """Get emergency contacts"""
        endpoint = ENDPOINTS['contacts']['list']
        response = self._make_request('GET', endpoint)
        return response.get('data', []) if response.get('success') else []
    
    def create_contact(self, contact_data):
        """Create emergency contact"""
        endpoint = ENDPOINTS['contacts']['create']
        return self._make_request('POST', endpoint, data=contact_data)
    
    def update_contact(self, contact_id, contact_data):
        """Update emergency contact"""
        endpoint = ENDPOINTS['contacts']['update'].format(contact_id)
        return self._make_request('PUT', endpoint, data=contact_data)
    
    def delete_contact(self, contact_id):
        """Delete emergency contact"""
        endpoint = ENDPOINTS['contacts']['delete'].format(contact_id)
        return self._make_request('DELETE', endpoint)
    
    def get_primary_contacts(self):
        """Get primary emergency contacts for SOS"""
        endpoint = ENDPOINTS['contacts']['primary']
        response = self._make_request('GET', endpoint)
        return response.get('data', []) if response.get('success') else []
    
    # SOS endpoints
    def trigger_sos(self, lat, lon, address=None, trigger_type='manual'):
        """Trigger SOS alert"""
        endpoint = ENDPOINTS['sos']['trigger']
        data = {
            'lat': lat,
            'lon': lon,
            'address': address,
            'trigger_type': trigger_type
        }
        return self._make_request('POST', endpoint, data=data)
    
    def cancel_sos(self, reason=None):
        """Cancel active SOS"""
        endpoint = ENDPOINTS['sos']['cancel']
        data = {'reason': reason} if reason else {}
        return self._make_request('POST', endpoint, data=data)
    
    def get_sos_status(self):
        """Get current SOS status"""
        endpoint = ENDPOINTS['sos']['status']
        return self._make_request('GET', endpoint)
    
    def get_sos_history(self, limit=10):
        """Get SOS history"""
        endpoint = ENDPOINTS['sos']['history']
        params = {'limit': limit}
        response = self._make_request('GET', endpoint, params=params)
        return response.get('data', []) if response.get('success') else []
    
    # Location endpoints
    def update_location(self, lat, lon, address=None, accuracy=None):
        """Update user location"""
        endpoint = ENDPOINTS['location']['update']
        data = {
            'lat': lat,
            'lon': lon,
            'address': address,
            'accuracy': accuracy
        }
        return self._make_request('POST', endpoint, data=data)
    
    def get_current_location(self):
        """Get current stored location"""
        endpoint = ENDPOINTS['location']['current']
        return self._make_request('GET', endpoint)
    
    def create_location_share(self, expires_hours=24):
        """Create location share"""
        endpoint = ENDPOINTS['location']['share']
        data = {'expires_hours': expires_hours}
        return self._make_request('POST', endpoint, data=data)
    
    def get_location_shares(self):
        """Get location shares"""
        endpoint = ENDPOINTS['location']['shares']
        response = self._make_request('GET', endpoint)
        return response.get('data', []) if response.get('success') else []
    
    def delete_location_share(self, share_id):
        """Delete location share"""
        endpoint = ENDPOINTS['location']['delete_share'].format(share_id)
        return self._make_request('DELETE', endpoint)
    
    # Check-in endpoints
    def start_checkin_timer(self, hours, minutes):
        """Start check-in timer"""
        endpoint = ENDPOINTS['checkin']['start']
        data = {'hours': hours, 'minutes': minutes}
        return self._make_request('POST', endpoint, data=data)
    
    def mark_checkin_safe(self, timer_id, message=None):
        """Mark check-in as safe"""
        endpoint = ENDPOINTS['checkin']['safe']
        data = {'timer_id': timer_id, 'message': message}
        return self._make_request('POST', endpoint, data=data)
    
    def get_checkin_status(self):
        """Get check-in status"""
        endpoint = ENDPOINTS['checkin']['status']
        return self._make_request('GET', endpoint)
    
    def get_checkin_history(self, limit=10):
        """Get check-in history"""
        endpoint = ENDPOINTS['checkin']['history']
        params = {'limit': limit}
        response = self._make_request('GET', endpoint, params=params)
        return response.get('data', []) if response.get('success') else []
    
    # Incident endpoints
    def create_incident(self, incident_data):
        """Create incident report"""
        endpoint = ENDPOINTS['incidents']['create']
        return self._make_request('POST', endpoint, data=incident_data)
    
    def get_incidents(self, limit=20):
        """Get incident reports"""
        endpoint = ENDPOINTS['incidents']['list']
        params = {'limit': limit}
        response = self._make_request('GET', endpoint, params=params)
        return response.get('data', []) if response.get('success') else []
    
    def update_incident(self, incident_id, incident_data):
        """Update incident report"""
        endpoint = ENDPOINTS['incidents']['update'].format(incident_id)
        return self._make_request('PUT', endpoint, data=incident_data)
    
    def delete_incident(self, incident_id):
        """Delete incident report"""
        endpoint = ENDPOINTS['incidents']['delete'].format(incident_id)
        return self._make_request('DELETE', endpoint)
    
    # Police endpoints
    def get_nearby_police(self, lat, lon, radius=5000):
        """Get nearby police stations"""
        endpoint = ENDPOINTS['police']['nearby']
        params = {'lat': lat, 'lon': lon, 'radius': radius}
        response = self._make_request('GET', endpoint, params=params, require_auth=False)
        return response.get('data', []) if response.get('success') else []
    
    def get_emergency_helplines(self):
        """Get emergency helplines"""
        endpoint = ENDPOINTS['police']['helplines']
        response = self._make_request('GET', endpoint, require_auth=False)
        return response.get('data', []) if response.get('success') else []
    
    def get_police_station_details(self, place_id):
        """Get police station details"""
        endpoint = ENDPOINTS['police']['station'].format(place_id)
        return self._make_request('GET', endpoint, require_auth=False)
    
    def get_directions(self, origin_lat, origin_lon, dest_lat, dest_lon):
        """Get directions to location"""
        endpoint = ENDPOINTS['police']['directions']
        params = {
            'lat': origin_lat,
            'lon': origin_lon,
            'destination_lat': dest_lat,
            'destination_lon': dest_lon
        }
        return self._make_request('GET', endpoint, params=params, require_auth=False)

# Add time import for retry delay
import time
