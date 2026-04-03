from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.animation import Animation
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.app import MDApp

class SplashScreen(Screen):
    """SafeHer splash screen with animated logo"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'splash'
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the splash screen UI"""
        # Main layout
        layout = MDBoxLayout(
            orientation='vertical',
            padding=(20, 40),
            spacing=20,
            md_bg_color=(0.05, 0.05, 0.1, 1)  # Dark background
        )
        
        # Logo container
        logo_container = MDBoxLayout(
            orientation='vertical',
            size_hint_y=0.6,
            adaptive_height=True,
            pos_hint={'center_x': 0.5}
        )
        
        # Shield icon (using text as placeholder - would be image in production)
        logo_text = MDLabel(
            text="🛡️",
            font_style='H1',
            halign='center',
            theme_text_color='Custom',
            text_color=(0.76, 0.09, 0.36, 1),  # Primary color
            size_hint_y=None,
            height=100
        )
        
        # App name
        app_name = MDLabel(
            text="SafeHer",
            font_style='H3',
            halign='center',
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1),  # White
            bold=True,
            size_hint_y=None,
            height=50
        )
        
        # Tagline
        tagline = MDLabel(
            text="Your safety, always.",
            font_style='Body1',
            halign='center',
            theme_text_color='Custom',
            text_color=(0.69, 0.74, 0.77, 1),  # Text secondary
            size_hint_y=None,
            height=30
        )
        
        logo_container.add_widget(logo_text)
        logo_container.add_widget(app_name)
        logo_container.add_widget(tagline)
        
        # Loading indicator
        loading_text = MDLabel(
            text="Loading...",
            font_style='Caption',
            halign='center',
            theme_text_color='Custom',
            text_color=(0.69, 0.74, 0.77, 1),
            size_hint_y=None,
            height=20
        )
        
        layout.add_widget(logo_container)
        layout.add_widget(loading_text)
        
        self.add_widget(layout)
        
        # Start animations
        self.animate_logo()
    
    def animate_logo(self):
        """Animate the logo appearance"""
        # Get the logo text widget
        logo_text = self.children[0].children[0].children[2]  # Logo text is the first child
        
        # Create fade-in animation
        fade_anim = Animation(opacity=0, duration=0)
        fade_anim += Animation(opacity=1, duration=0.5)
        
        # Create scale animation
        scale_anim = Animation(scale_x=0.8, scale_y=0.8, duration=0)
        scale_anim += Animation(scale_x=1.0, scale_y=1.0, duration=0.5)
        
        # Start animations
        fade_anim.start(logo_text)
        scale_anim.start(logo_text)
        
        # Schedule navigation after 2.5 seconds
        Clock.schedule_once(self.navigate_to_welcome, 2.5)
    
    def navigate_to_welcome(self, dt):
        """Navigate to welcome screen"""
        app = MDApp.get_running_app()
        if hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'welcome'
