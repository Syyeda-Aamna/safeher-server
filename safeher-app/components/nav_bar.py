from kivymd.uix.bottomnavigation import MDBottomNavigation
from kivymd.uix.bottomnavigationitem import MDBottomNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.app import MDApp
from config import COLORS

class BottomNavBar(MDBottomNavigation):
    """Custom bottom navigation bar for SafeHer app"""
    
    def __init__(self, current_tab='home', **kwargs):
        super().__init__(**kwargs)
        self.current_tab = current_tab
        self.setup_navigation()
    
    def setup_navigation(self):
        """Setup bottom navigation items"""
        # Navigation items configuration
        nav_items = [
            {
                'name': 'home',
                'text': 'Home',
                'icon': 'home',
                'screen': 'dashboard'
            },
            {
                'name': 'contacts',
                'text': 'Contacts',
                'icon': 'contacts',
                'screen': 'contacts'
            },
            {
                'name': 'map',
                'text': 'Map',
                'icon': 'map',
                'screen': 'map'
            },
            {
                'name': 'profile',
                'text': 'Profile',
                'icon': 'account',
                'screen': 'settings'
            }
        ]
        
        # Create navigation items
        for item_config in nav_items:
            nav_item = MDBottomNavigationItem(
                name=item_config['name'],
                text=item_config['text'],
                icon=item_config['icon'],
                on_tab_press=lambda x, screen=item_config['screen']: self.navigate_to_screen(screen)
            )
            
            # Set active state
            if item_config['name'] == self.current_tab:
                nav_item.active = True
                nav_item.text_color = COLORS['primary']
                nav_item.icon_color = COLORS['primary']
            else:
                nav_item.text_color = COLORS['text_secondary']
                nav_item.icon_color = COLORS['text_secondary']
            
            self.add_widget(nav_item)
    
    def navigate_to_screen(self, screen_name):
        """Navigate to specified screen"""
        app = MDApp.get_running_app()
        if hasattr(app, 'screen_manager'):
            app.screen_manager.current = screen_name
            
            # Update active tab
            self.set_active_tab(screen_name)
    
    def set_active_tab(self, screen_name):
        """Set active tab based on screen name"""
        # Map screen names to tab names
        screen_to_tab = {
            'dashboard': 'home',
            'contacts': 'contacts',
            'map': 'map',
            'settings': 'profile'
        }
        
        tab_name = screen_to_tab.get(screen_name)
        if not tab_name:
            return
        
        # Update all navigation items
        for item in self.children:
            if hasattr(item, 'name'):
                if item.name == tab_name:
                    item.active = True
                    item.text_color = COLORS['primary']
                    item.icon_color = COLORS['primary']
                else:
                    item.active = False
                    item.text_color = COLORS['text_secondary']
                    item.icon_color = COLORS['text_secondary']
    
    def on_tab_press(self, instance, value):
        """Handle tab press"""
        # This is already handled in the setup_navigation method
        pass

class CustomBottomNavigationItem(MDBottomNavigationItem):
    """Custom bottom navigation item with enhanced styling"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_custom_style()
    
    def setup_custom_style(self):
        """Setup custom styling for navigation item"""
        # Custom colors and styling
        self.text_color = COLORS['text_secondary']
        self.icon_color = COLORS['text_secondary']
        
        # Active state colors
        if hasattr(self, 'active') and self.active:
            self.text_color = COLORS['primary']
            self.icon_color = COLORS['primary']
        
        # Font styling
        self.font_style = 'Caption'
        
        # Size adjustments
        self.height = 56  # Standard bottom nav height
        self.padding = (8, 4)
    
    def on_active(self, instance, value):
        """Handle active state change"""
        if value:
            self.text_color = COLORS['primary']
            self.icon_color = COLORS['primary']
        else:
            self.text_color = COLORS['text_secondary']
            self.icon_color = COLORS['text_secondary']

class BottomNavBarWithBadge(MDBottomNavigation):
    """Bottom navigation bar with notification badges"""
    
    def __init__(self, current_tab='home', **kwargs):
        super().__init__(**kwargs)
        self.current_tab = current_tab
        self.badge_counts = {}
        self.setup_navigation_with_badges()
    
    def setup_navigation_with_badges(self):
        """Setup navigation with badge support"""
        # Navigation items with badges
        nav_items = [
            {
                'name': 'home',
                'text': 'Home',
                'icon': 'home',
                'screen': 'dashboard',
                'badge_key': 'sos_alerts'
            },
            {
                'name': 'contacts',
                'text': 'Contacts',
                'icon': 'contacts',
                'screen': 'contacts',
                'badge_key': 'contact_requests'
            },
            {
                'name': 'map',
                'text': 'Map',
                'icon': 'map',
                'screen': 'map',
                'badge_key': None
            },
            {
                'name': 'profile',
                'text': 'Profile',
                'icon': 'account',
                'screen': 'settings',
                'badge_key': 'updates'
            }
        ]
        
        for item_config in nav_items:
            nav_item = CustomBottomNavigationItem(
                name=item_config['name'],
                text=item_config['text'],
                icon=item_config['icon'],
                on_tab_press=lambda x, screen=item_config['screen']: self.navigate_to_screen(screen)
            )
            
            # Set badge if applicable
            if item_config['badge_key']:
                self.set_badge(item_config['name'], 0)  # Initialize with 0
            
            # Set active state
            if item_config['name'] == self.current_tab:
                nav_item.active = True
                nav_item.text_color = COLORS['primary']
                nav_item.icon_color = COLORS['primary']
            
            self.add_widget(nav_item)
    
    def set_badge(self, tab_name, count):
        """Set badge count for tab"""
        self.badge_counts[tab_name] = count
        
        # Update the navigation item
        for item in self.children:
            if hasattr(item, 'name') and item.name == tab_name:
                # Update badge display (implementation depends on UI framework)
                if hasattr(item, 'badge_text'):
                    item.badge_text = str(count) if count > 0 else ''
                elif hasattr(item, 'badge_count'):
                    item.badge_count = count
                break
    
    def increment_badge(self, tab_name):
        """Increment badge count"""
        current_count = self.badge_counts.get(tab_name, 0)
        self.set_badge(tab_name, current_count + 1)
    
    def clear_badge(self, tab_name):
        """Clear badge for tab"""
        self.set_badge(tab_name, 0)
    
    def navigate_to_screen(self, screen_name):
        """Navigate to specified screen"""
        app = MDApp.get_running_app()
        if hasattr(app, 'screen_manager'):
            app.screen_manager.current = screen_name
            self.set_active_tab(screen_name)
            
            # Clear badge for home tab when navigating to it
            if screen_name == 'dashboard':
                self.clear_badge('home')
    
    def set_active_tab(self, screen_name):
        """Set active tab based on screen name"""
        screen_to_tab = {
            'dashboard': 'home',
            'contacts': 'contacts',
            'map': 'map',
            'settings': 'profile'
        }
        
        tab_name = screen_to_tab.get(screen_name)
        if not tab_name:
            return
        
        for item in self.children:
            if hasattr(item, 'name'):
                if item.name == tab_name:
                    item.active = True
                    item.text_color = COLORS['primary']
                    item.icon_color = COLORS['primary']
                else:
                    item.active = False
                    item.text_color = COLORS['text_secondary']
                    item.icon_color = COLORS['text_secondary']
