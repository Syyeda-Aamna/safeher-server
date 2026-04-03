import os
import sys
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.theming import ThemeManager

# Import screens
from screens.splash import SplashScreen
from screens.welcome import WelcomeScreen
from screens.register import RegisterScreen
from screens.otp_verify import OTPVerifyScreen
from screens.login import LoginScreen
from screens.dashboard import DashboardScreen
from screens.sos_active import SOSActiveScreen
from screens.contacts import ContactsScreen
from screens.emergency_call import EmergencyCallScreen
from screens.map_screen import MapScreen
from screens.police_stations import PoliceStationsScreen
from screens.checkin import CheckinScreen
from screens.location_share import LocationShareScreen
from screens.sos_history import SOSHistoryScreen
from screens.incident import IncidentScreen
from screens.tips import TipsScreen
from screens.settings import SettingsScreen

# Import services
from services.local_db import LocalDB
from services.api_client import APIClient
from services.location_service import LocationService
from services.shake_service import ShakeService

# Import components
from components.nav_bar import BottomNavBar
from components.sos_button import SOSButton

class SafeHerApp(MDApp):
    """SafeHer Women Safety App"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Pink"
        self.theme_cls.theme_style = "Dark"
        
        # Custom colors for SafeHer branding
        self.theme_cls.colors = {
            'primary': '#C2185B',
            'secondary': '#7B1FA2',
            'accent': '#FF4081',
            'background': '#0D0D1A',
            'surface': '#1A1A2E',
            'surface_variant': '#16213E',
            'on_primary': '#FFFFFF',
            'on_secondary': '#FFFFFF',
            'on_surface': '#FFFFFF',
            'on_background': '#FFFFFF',
            'success': '#00E676',
            'warning': '#FFD740',
            'error': '#FF1744',
            'text_secondary': '#B0BEC5'
        }
        
        # App state
        self.user_data = None
        self.jwt_token = None
        self.current_location = None
        self.emergency_contacts = []
        self.sos_active = False
        
        # Services
        self.local_db = LocalDB()
        self.api_client = APIClient()
        self.location_service = LocationService()
        self.shake_service = ShakeService()
        
        # Screen manager
        self.screen_manager = None
        
    def build(self):
        """Build the app"""
        # Set window properties
        Window.size = (360, 640)  # Standard mobile size
        Window.clearcolor = (0.05, 0.05, 0.1, 1)  # Dark background
        
        # Create screen manager
        self.screen_manager = ScreenManager()
        
        # Add all screens
        screens = [
            SplashScreen(name='splash'),
            WelcomeScreen(name='welcome'),
            RegisterScreen(name='register'),
            OTPVerifyScreen(name='otp_verify'),
            LoginScreen(name='login'),
            DashboardScreen(name='dashboard'),
            SOSActiveScreen(name='sos_active'),
            ContactsScreen(name='contacts'),
            EmergencyCallScreen(name='emergency_call'),
            MapScreen(name='map'),
            PoliceStationsScreen(name='police_stations'),
            CheckinScreen(name='checkin'),
            LocationShareScreen(name='location_share'),
            SOSHistoryScreen(name='sos_history'),
            IncidentScreen(name='incident'),
            TipsScreen(name='tips'),
            SettingsScreen(name='settings')
        ]
        
        for screen in screens:
            self.screen_manager.add_widget(screen)
        
        # Initialize services
        self.initialize_services()
        
        # Load user data if available
        self.load_user_session()
        
        # Schedule periodic location updates
        Clock.schedule_interval(self.update_location, 60)  # Every minute
        
        return self.screen_manager
    
    def initialize_services(self):
        """Initialize all services"""
        try:
            # Initialize local database
            self.local_db.initialize()
            
            # Initialize location service
            self.location_service.initialize()
            
            # Initialize shake service
            self.shake_service.initialize()
            
            print("Services initialized successfully")
            
        except Exception as e:
            print(f"Error initializing services: {e}")
    
    def load_user_session(self):
        """Load saved user session"""
        try:
            user_data = self.local_db.get_user()
            if user_data and user_data.get('jwt_token'):
                self.user_data = user_data
                self.jwt_token = user_data['jwt_token']
                self.api_client.set_token(self.jwt_token)
                
                # Load emergency contacts
                self.emergency_contacts = self.local_db.get_contacts()
                
                # Go to dashboard if user is logged in
                self.screen_manager.current = 'dashboard'
                print(f"User session loaded: {user_data.get('full_name')}")
            else:
                # Show splash screen first
                self.screen_manager.current = 'splash'
                # Auto-redirect to welcome after 2.5 seconds
                Clock.schedule_once(lambda dt: self.go_to_welcome(), 2.5)
                
        except Exception as e:
            print(f"Error loading user session: {e}")
            self.screen_manager.current = 'splash'
            Clock.schedule_once(lambda dt: self.go_to_welcome(), 2.5)
    
    def go_to_welcome(self):
        """Navigate to welcome screen"""
        self.screen_manager.current = 'welcome'
    
    def login_user(self, user_data, jwt_token):
        """Handle user login"""
        try:
            self.user_data = user_data
            self.jwt_token = jwt_token
            
            # Save to local database
            self.local_db.save_user(user_data, jwt_token)
            
            # Set API client token
            self.api_client.set_token(jwt_token)
            
            # Load emergency contacts
            self.emergency_contacts = self.local_db.get_contacts()
            
            # Navigate to dashboard
            self.screen_manager.current = 'dashboard'
            
            print(f"User logged in: {user_data.get('full_name')}")
            
        except Exception as e:
            print(f"Error during login: {e}")
            self.show_error("Login failed. Please try again.")
    
    def logout_user(self):
        """Handle user logout"""
        try:
            # Clear local data
            self.local_db.clear_user_data()
            
            # Clear app state
            self.user_data = None
            self.jwt_token = None
            self.emergency_contacts = []
            
            # Clear API client token
            self.api_client.set_token(None)
            
            # Navigate to welcome screen
            self.screen_manager.current = 'welcome'
            
            print("User logged out successfully")
            
        except Exception as e:
            print(f"Error during logout: {e}")
    
    def update_location(self, dt):
        """Update current location periodically"""
        try:
            if self.jwt_token:  # Only update if user is logged in
                location = self.location_service.get_current_location()
                if location:
                    self.current_location = location
                    # Send to server
                    self.api_client.update_location(
                        location['lat'], 
                        location['lon'], 
                        location.get('address')
                    )
                    
        except Exception as e:
            print(f"Error updating location: {e}")
    
    def trigger_sos(self, trigger_type='manual'):
        """Trigger SOS alert"""
        try:
            if self.sos_active:
                return  # SOS already active
            
            if not self.emergency_contacts:
                self.show_error("No emergency contacts found. Please add contacts first.")
                return
            
            if not self.current_location:
                self.show_error("Location not available. Please enable GPS.")
                return
            
            self.sos_active = True
            
            # Send SOS to server
            response = self.api_client.trigger_sos(
                self.current_location['lat'],
                self.current_location['lon'],
                self.current_location.get('address'),
                trigger_type
            )
            
            if response and response.get('id'):
                # Navigate to SOS active screen
                self.screen_manager.current = 'sos_active'
                print(f"SOS triggered: {response['id']}")
            else:
                self.sos_active = False
                self.show_error("Failed to trigger SOS. Please try again.")
                
        except Exception as e:
            self.sos_active = False
            print(f"Error triggering SOS: {e}")
            self.show_error("Failed to trigger SOS. Please try again.")
    
    def cancel_sos(self):
        """Cancel active SOS"""
        try:
            response = self.api_client.cancel_sos()
            if response:
                self.sos_active = False
                self.screen_manager.current = 'dashboard'
                print("SOS cancelled successfully")
            else:
                self.show_error("Failed to cancel SOS. Please try again.")
                
        except Exception as e:
            print(f"Error cancelling SOS: {e}")
            self.show_error("Failed to cancel SOS. Please try again.")
    
    def show_error(self, message):
        """Show error message"""
        # This would show a snackbar or toast in the UI
        print(f"Error: {message}")
        # Implementation would use MDSnackbar
    
    def show_success(self, message):
        """Show success message"""
        # This would show a snackbar or toast in the UI
        print(f"Success: {message}")
        # Implementation would use MDSnackbar

if __name__ == '__main__':
    SafeHerApp().run()
