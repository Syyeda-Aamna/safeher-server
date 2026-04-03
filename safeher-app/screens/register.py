from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDTextButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.app import MDApp
from kivy.metrics import dp

class RegisterScreen(Screen):
    """User registration screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'register'
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the registration screen UI"""
        # Main layout
        main_layout = MDBoxLayout(
            orientation='vertical',
            padding=(20, 40),
            spacing=20,
            md_bg_color=(0.05, 0.05, 0.1, 1)  # Dark background
        )
        
        # Header
        header = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=80,
            spacing=10
        )
        
        title = MDLabel(
            text="Create Account",
            font_style='H4',
            halign='center',
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1),
            bold=True,
            size_hint_y=None,
            height=40
        )
        
        subtitle = MDLabel(
            text="Join SafeHer for your safety",
            font_style='Body1',
            halign='center',
            theme_text_color='Custom',
            text_color=(0.69, 0.74, 0.77, 1),
            size_hint_y=None,
            height=30
        )
        
        header.add_widget(title)
        header.add_widget(subtitle)
        
        # Registration form card
        form_card = MDCard(
            orientation='vertical',
            padding=20,
            spacing=15,
            radius=[16, 16, 16, 16],
            md_bg_color=(0.1, 0.1, 0.18, 1),  # Surface color
            elevation=4
        )
        
        # Full Name field
        self.name_field = MDTextField(
            hint_text="Full Name",
            mode="rectangle",
            size_hint_y=None,
            height=50,
            font_size=16,
            icon_left="account",
            icon_left_color=(0.76, 0.09, 0.36, 1),
            line_color_normal=(0.69, 0.74, 0.77, 0.5),
            line_color_focus=(0.76, 0.09, 0.36, 1)
        )
        
        # Phone field
        self.phone_field = MDTextField(
            hint_text="Phone Number",
            mode="rectangle",
            size_hint_y=None,
            height=50,
            font_size=16,
            icon_left="phone",
            icon_left_color=(0.76, 0.09, 0.36, 1),
            line_color_normal=(0.69, 0.74, 0.77, 0.5),
            line_color_focus=(0.76, 0.09, 0.36, 1),
            helper_text="Enter 10-digit mobile number",
            helper_text_mode="on_focus"
        )
        
        # Email field
        self.email_field = MDTextField(
            hint_text="Email (Optional)",
            mode="rectangle",
            size_hint_y=None,
            height=50,
            font_size=16,
            icon_left="email",
            icon_left_color=(0.76, 0.09, 0.36, 1),
            line_color_normal=(0.69, 0.74, 0.77, 0.5),
            line_color_focus=(0.76, 0.09, 0.36, 1)
        )
        
        # Password field
        self.password_field = MDTextField(
            hint_text="Password",
            mode="rectangle",
            size_hint_y=None,
            height=50,
            font_size=16,
            password=True,
            icon_left="lock",
            icon_left_color=(0.76, 0.09, 0.36, 1),
            line_color_normal=(0.69, 0.74, 0.77, 0.5),
            line_color_focus=(0.76, 0.09, 0.36, 1),
            helper_text="Min 8 characters with uppercase, lowercase, and digit",
            helper_text_mode="on_focus"
        )
        
        # Confirm Password field
        self.confirm_password_field = MDTextField(
            hint_text="Confirm Password",
            mode="rectangle",
            size_hint_y=None,
            height=50,
            font_size=16,
            password=True,
            icon_left="lock-check",
            icon_left_color=(0.76, 0.09, 0.36, 1),
            line_color_normal=(0.69, 0.74, 0.77, 0.5),
            line_color_focus=(0.76, 0.09, 0.36, 1)
        )
        
        form_card.add_widget(self.name_field)
        form_card.add_widget(self.phone_field)
        form_card.add_widget(self.email_field)
        form_card.add_widget(self.password_field)
        form_card.add_widget(self.confirm_password_field)
        
        # Send OTP button
        self.send_otp_btn = MDRaisedButton(
            text="Send OTP",
            font_style='Button',
            size_hint=(1, None),
            height=50,
            md_bg_color=(0.76, 0.09, 0.36, 1),  # Primary color
            text_color=(1, 1, 1, 1),
            on_release=self.send_otp
        )
        
        form_card.add_widget(self.send_otp_btn)
        
        # Login link
        login_link = MDTextButton(
            text="Already have an account? Login",
            font_style='Body1',
            halign='center',
            theme_text_color='Custom',
            text_color=(0.76, 0.09, 0.36, 1),
            size_hint_y=None,
            height=30,
            on_release=self.go_to_login
        )
        
        # Add all widgets to main layout
        main_layout.add_widget(header)
        main_layout.add_widget(form_card)
        main_layout.add_widget(login_link)
        
        self.add_widget(main_layout)
    
    def send_otp(self, instance):
        """Send OTP for registration"""
        # Get form values
        name = self.name_field.text.strip()
        phone = self.phone_field.text.strip()
        email = self.email_field.text.strip()
        password = self.password_field.text
        confirm_password = self.confirm_password_field.text
        
        # Validation
        if not name:
            self.show_error("Please enter your full name")
            return
        
        if not phone or len(phone) != 10 or not phone.startswith(('6', '7', '8', '9')):
            self.show_error("Please enter a valid 10-digit mobile number")
            return
        
        if email and '@' not in email:
            self.show_error("Please enter a valid email address")
            return
        
        if not password or len(password) < 8:
            self.show_error("Password must be at least 8 characters long")
            return
        
        if password != confirm_password:
            self.show_error("Passwords do not match")
            return
        
        # Check password strength
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            self.show_error("Password must contain uppercase, lowercase, and digit")
            return
        
        # Show loading state
        self.send_otp_btn.text = "Sending..."
        self.send_otp_btn.disabled = True
        
        # Send registration request to API
        app = MDApp.get_running_app()
        if hasattr(app, 'api_client'):
            # Store registration data temporarily
            self.registration_data = {
                'full_name': name,
                'phone': phone,
                'email': email if email else None,
                'password': password
            }
            
            # Call API (this would be implemented in api_client)
            response = app.api_client.register_user(self.registration_data)
            
            if response and response.get('success'):
                self.show_success("OTP sent successfully!")
                # Navigate to OTP verification screen
                Clock.schedule_once(lambda dt: self.go_to_otp_verification(), 1)
            else:
                self.show_error(response.get('message', 'Registration failed'))
        
        # Reset button state
        self.send_otp_btn.text = "Send OTP"
        self.send_otp_btn.disabled = False
    
    def go_to_otp_verification(self):
        """Navigate to OTP verification screen"""
        app = MDApp.get_running_app()
        if hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'otp_verify'
    
    def go_to_login(self, instance):
        """Navigate to login screen"""
        app = MDApp.get_running_app()
        if hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'login'
    
    def show_error(self, message):
        """Show error message"""
        app = MDApp.get_running_app()
        if hasattr(app, 'show_error'):
            app.show_error(message)
    
    def show_success(self, message):
        """Show success message"""
        app = MDApp.get_running_app()
        if hasattr(app, 'show_success'):
            app.show_success(message)
