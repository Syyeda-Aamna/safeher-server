from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDTextButton
from kivymd.app import MDApp

class WelcomeScreen(Screen):
    """Welcome screen for SafeHer app"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'welcome'
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the welcome screen UI"""
        # Main layout with gradient background
        layout = MDBoxLayout(
            orientation='vertical',
            padding=(20, 40),
            spacing=30,
            md_bg_color=(0.05, 0.05, 0.1, 1)  # Dark background
        )
        
        # Top illustration area
        illustration_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_y=0.4,
            adaptive_height=True,
            pos_hint={'center_x': 0.5}
        )
        
        # Shield illustration (emoji placeholder)
        shield_emoji = MDLabel(
            text="🛡️",
            font_style='H1',
            halign='center',
            theme_text_color='Custom',
            text_color=(0.76, 0.09, 0.36, 1),  # Primary color
            size_hint_y=None,
            height=120
        )
        
        illustration_layout.add_widget(shield_emoji)
        
        # Welcome text section
        welcome_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_y=0.3,
            spacing=15,
            pos_hint={'center_x': 0.5}
        )
        
        welcome_title = MDLabel(
            text="Welcome to SafeHer",
            font_style='H4',
            halign='center',
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1),  # White
            bold=True,
            size_hint_y=None,
            height=40
        )
        
        welcome_subtitle = MDLabel(
            text="Your personal safety companion\nEmpowering women with instant help at your fingertips",
            font_style='Body1',
            halign='center',
            theme_text_color='Custom',
            text_color=(0.69, 0.74, 0.77, 1),  # Text secondary
            size_hint_y=None,
            height=60
        )
        
        welcome_layout.add_widget(welcome_title)
        welcome_layout.add_widget(welcome_subtitle)
        
        # Buttons section
        buttons_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_y=0.3,
            spacing=20,
            pos_hint={'center_x': 0.5}
        )
        
        # Create Account button
        create_account_btn = MDRaisedButton(
            text="Create Account",
            font_style='Button',
            size_hint=(0.8, None),
            height=50,
            pos_hint={'center_x': 0.5},
            md_bg_color=(0.76, 0.09, 0.36, 1),  # Primary color
            text_color=(1, 1, 1, 1),
            on_release=self.go_to_register
        )
        
        # Login button
        login_btn = MDTextButton(
            text="Login",
            font_style='Button',
            size_hint=(0.8, None),
            height=50,
            pos_hint={'center_x': 0.5},
            text_color=(0.76, 0.09, 0.36, 1),  # Primary color
            on_release=self.go_to_login
        )
        
        buttons_layout.add_widget(create_account_btn)
        buttons_layout.add_widget(login_btn)
        
        # Emergency helplines link
        helplines_btn = MDTextButton(
            text="Emergency Helplines (no login needed)",
            font_style='Caption',
            size_hint=(None, None),
            height=30,
            pos_hint={'center_x': 0.5},
            text_color=(0.69, 0.74, 0.77, 1),
            on_release=self.go_to_emergency_helplines
        )
        
        # Add all layouts to main layout
        layout.add_widget(illustration_layout)
        layout.add_widget(welcome_layout)
        layout.add_widget(buttons_layout)
        layout.add_widget(helplines_btn)
        
        self.add_widget(layout)
    
    def go_to_register(self, instance):
        """Navigate to registration screen"""
        app = MDApp.get_running_app()
        if hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'register'
    
    def go_to_login(self, instance):
        """Navigate to login screen"""
        app = MDApp.get_running_app()
        if hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'login'
    
    def go_to_emergency_helplines(self, instance):
        """Navigate to emergency helplines"""
        app = MDApp.get_running_app()
        if hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'emergency_call'
