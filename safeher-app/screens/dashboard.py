from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.animation import Animation
from components.sos_button import SOSButton
from components.nav_bar import BottomNavBar

class DashboardScreen(Screen):
    """Main dashboard screen with SOS button and features"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'dashboard'
        self.sos_button = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dashboard UI"""
        # Main layout
        main_layout = MDBoxLayout(
            orientation='vertical',
            md_bg_color=(0.05, 0.05, 0.1, 1)  # Dark background
        )
        
        # Header with greeting
        header_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=60,
            padding=(20, 10),
            md_bg_color=(0.76, 0.09, 0.36, 1),  # Primary gradient
            spacing=10
        )
        
        app = MDApp.get_running_app()
        user_name = app.user_data.get('full_name', 'User') if app.user_data else 'User'
        greeting_text = f"Hi, {user_name.split()[0]} 👋"
        
        greeting_label = MDLabel(
            text=greeting_text,
            font_style='H6',
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1),
            size_hint_x=0.8
        )
        
        # GPS status indicator
        gps_status = MDIconButton(
            icon="map-marker",
            theme_text_color='Custom',
            text_color=(0, 1, 0, 1),  # Green
            size_hint_x=0.2,
            pos_hint={'center_y': 0.5}
        )
        
        header_layout.add_widget(greeting_label)
        header_layout.add_widget(gps_status)
        
        # Content area
        content_layout = MDBoxLayout(
            orientation='vertical',
            padding=20,
            spacing=20
        )
        
        # SOS Button Section
        sos_section = MDBoxLayout(
            orientation='vertical',
            size_hint_y=0.4,
            adaptive_height=True,
            pos_hint={'center_x': 0.5},
            spacing=10
        )
        
        # Create SOS button
        self.sos_button = SOSButton(
            size_hint=(None, None),
            size=(140, 140),
            pos_hint={'center_x': 0.5},
            on_release=self.trigger_sos
        )
        
        # SOS caption
        sos_caption = MDLabel(
            text="Hold for emergency",
            font_style='Caption',
            halign='center',
            theme_text_color='Custom',
            text_color=(0.69, 0.74, 0.77, 1),
            size_hint_y=None,
            height=20
        )
        
        sos_section.add_widget(self.sos_button)
        sos_section.add_widget(sos_caption)
        
        # Quick Actions Row
        quick_actions = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=80,
            spacing=15,
            pos_hint={'center_x': 0.5}
        )
        
        # Quick action buttons
        actions = [
            {"icon": "phone", "label": "Call", "callback": self.go_to_emergency_call},
            {"icon": "map", "label": "Map", "callback": self.go_to_map},
            {"icon": "contacts", "label": "Contacts", "callback": self.go_to_contacts},
            {"icon": "police", "label": "Police", "callback": self.go_to_police}
        ]
        
        for action in actions:
            action_card = MDCard(
                size_hint_x=0.25,
                size_hint_y=None,
                height=70,
                radius=[12, 12, 12, 12],
                md_bg_color=(0.1, 0.1, 0.18, 1),  # Surface color
                elevation=4
            )
            
            action_layout = MDBoxLayout(
                orientation='vertical',
                padding=10,
                spacing=5
            )
            
            icon_btn = MDIconButton(
                icon=action["icon"],
                theme_text_color='Custom',
                text_color=(0.76, 0.09, 0.36, 1),  # Primary color
                size_hint=(None, None),
                size=(30, 30),
                pos_hint={'center_x': 0.5}
            )
            
            label = MDLabel(
                text=action["label"],
                font_style='Caption',
                halign='center',
                theme_text_color='Custom',
                text_color=(1, 1, 1, 1),
                size_hint_y=None,
                height=15
            )
            
            action_layout.add_widget(icon_btn)
            action_layout.add_widget(label)
            action_card.add_widget(action_layout)
            
            # Make the whole card clickable
            action_card.bind(on_release=action["callback"])
            quick_actions.add_widget(action_card)
        
        # Feature Grid
        features_grid = MDGridLayout(
            cols=2,
            spacing=15,
            size_hint_y=0.4,
            pos_hint={'center_x': 0.5}
        )
        
        # Feature tiles
        features = [
            {"icon": "route", "title": "Safe Route", "subtitle": "Find safe paths"},
            {"icon": "timer", "title": "Check-In", "subtitle": "Timer safety"},
            {"icon": "location", "title": "Live Location", "subtitle": "Share location"},
            {"icon": "alert", "title": "Incident Report", "subtitle": "Report issues"},
            {"icon": "phone-classic", "title": "Helplines", "subtitle": "Emergency numbers"},
            {"icon": "history", "title": "SOS History", "subtitle": "Past alerts"},
            {"icon": "lightbulb", "title": "Safety Tips", "subtitle": "Stay informed"},
            {"icon": "cog", "title": "Settings", "subtitle": "App preferences"}
        ]
        
        for feature in features:
            feature_card = MDCard(
                size_hint=(None, None),
                size=(150, 100),
                radius=[16, 16, 16, 16],
                md_bg_color=(0.1, 0.1, 0.18, 1),  # Surface color
                elevation=3
            )
            
            feature_layout = MDBoxLayout(
                orientation='vertical',
                padding=15,
                spacing=8
            )
            
            icon = MDIconButton(
                icon=feature["icon"],
                theme_text_color='Custom',
                text_color=(0.76, 0.09, 0.36, 1),  # Primary color
                size_hint=(None, None),
                size=(30, 30)
            )
            
            title = MDLabel(
                text=feature["title"],
                font_style='Button',
                theme_text_color='Custom',
                text_color=(1, 1, 1, 1),
                size_hint_y=None,
                height=20
            )
            
            subtitle = MDLabel(
                text=feature["subtitle"],
                font_style='Caption',
                theme_text_color='Custom',
                text_color=(0.69, 0.74, 0.77, 1),
                size_hint_y=None,
                height=15
            )
            
            feature_layout.add_widget(icon)
            feature_layout.add_widget(title)
            feature_layout.add_widget(subtitle)
            feature_card.add_widget(feature_layout)
            
            # Add click handlers based on feature
            feature_handlers = {
                "Safe Route": self.go_to_map,
                "Check-In": self.go_to_checkin,
                "Live Location": self.go_to_location_share,
                "Incident Report": self.go_to_incident,
                "Helplines": self.go_to_emergency_call,
                "SOS History": self.go_to_sos_history,
                "Safety Tips": self.go_to_tips,
                "Settings": self.go_to_settings
            }
            
            if feature["title"] in feature_handlers:
                feature_card.bind(on_release=feature_handlers[feature["title"]])
            
            features_grid.add_widget(feature_card)
        
        # Add all sections to content layout
        content_layout.add_widget(sos_section)
        content_layout.add_widget(quick_actions)
        content_layout.add_widget(features_grid)
        
        # Bottom Navigation
        bottom_nav = BottomNavBar(current_tab='home')
        
        # Add everything to main layout
        main_layout.add_widget(header_layout)
        main_layout.add_widget(content_layout)
        main_layout.add_widget(bottom_nav)
        
        self.add_widget(main_layout)
        
        # Start animations
        self.animate_elements()
    
    def animate_elements(self):
        """Animate dashboard elements on load"""
        # Animate SOS button
        if self.sos_button:
            anim = Animation(scale_x=0.8, scale_y=0.8, duration=0)
            anim += Animation(scale_x=1.0, scale_y=1.0, duration=0.5)
            anim.start(self.sos_button)
    
    def trigger_sos(self, instance):
        """Trigger SOS alert"""
        app = MDApp.get_running_app()
        if hasattr(app, 'trigger_sos'):
            app.trigger_sos()
    
    def go_to_emergency_call(self, instance):
        """Navigate to emergency call screen"""
        app = MDApp.get_running_app()
        if hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'emergency_call'
    
    def go_to_map(self, instance):
        """Navigate to map screen"""
        app = MDApp.get_running_app()
        if hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'map'
    
    def go_to_contacts(self, instance):
        """Navigate to contacts screen"""
        app = MDApp.get_running_app()
        if hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'contacts'
    
    def go_to_police(self, instance):
        """Navigate to police stations screen"""
        app = MDApp.get_running_app()
        if hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'police_stations'
    
    def go_to_checkin(self, instance):
        """Navigate to check-in screen"""
        app = MDApp.get_running_app()
        if hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'checkin'
    
    def go_to_location_share(self, instance):
        """Navigate to location share screen"""
        app = MDApp.get_running_app()
        if hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'location_share'
    
    def go_to_incident(self, instance):
        """Navigate to incident screen"""
        app = MDApp.get_running_app()
        if hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'incident'
    
    def go_to_sos_history(self, instance):
        """Navigate to SOS history screen"""
        app = MDApp.get_running_app()
        if hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'sos_history'
    
    def go_to_tips(self, instance):
        """Navigate to safety tips screen"""
        app = MDApp.get_running_app()
        if hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'tips'
    
    def go_to_settings(self, instance):
        """Navigate to settings screen"""
        app = MDApp.get_running_app()
        if hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'settings'
