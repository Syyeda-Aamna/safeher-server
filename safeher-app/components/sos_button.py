from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import BooleanProperty, NumericProperty
from kivymd.app import MDApp
from config import COLORS

class SOSButton(MDRaisedButton):
    """Animated SOS button with pulse effect"""
    
    is_active = BooleanProperty(False)
    pulse_animation = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_button()
        self.start_pulse_animation()
    
    def setup_button(self):
        """Setup SOS button appearance"""
        # Button properties
        self.md_bg_color = COLORS['error']  # Red color for SOS
        self.text_color = (1, 1, 1, 1)  # White text
        self.font_style = 'H3'
        self.text = "SOS"
        self.elevation = 8
        self.radius = [70, 70, 70, 70]  # Circular button
        
        # Make button square
        self.size_hint = (None, None)
        self.width = 140
        self.height = 140
    
    def start_pulse_animation(self):
        """Start pulsing animation"""
        # Create pulse animation
        self.pulse_animation = Animation(
            elevation=12, 
            duration=0.8
        ) + Animation(
            elevation=8, 
            duration=0.8
        )
        
        # Loop the animation
        self.pulse_animation.repeat = True
        self.pulse_animation.start(self)
    
    def stop_pulse_animation(self):
        """Stop pulsing animation"""
        if self.pulse_animation:
            self.pulse_animation.cancel(self)
            self.elevation = 8
    
    def on_press(self):
        """Handle button press"""
        super().on_press()
        
        # Visual feedback
        press_animation = Animation(
            scale_x=0.95, 
            scale_y=0.95, 
            duration=0.1
        )
        press_animation.start(self)
        
        # Haptic feedback (if available)
        self.trigger_haptic_feedback()
    
    def on_release(self):
        """Handle button release"""
        super().on_release()
        
        # Visual feedback
        release_animation = Animation(
            scale_x=1.0, 
            scale_y=1.0, 
            duration=0.1
        )
        release_animation.start(self)
    
    def set_active(self, active: bool):
        """Set SOS button active state"""
        self.is_active = active
        
        if active:
            # Change appearance for active state
            self.md_bg_color = COLORS['error']  # Bright red
            self.text = "ACTIVE"
            self.stop_pulse_animation()
            
            # Add glow effect
            active_animation = Animation(
                elevation=15,
                duration=0.3
            )
            active_animation.start(self)
        else:
            # Reset to normal state
            self.md_bg_color = COLORS['error']
            self.text = "SOS"
            self.elevation = 8
            self.start_pulse_animation()
    
    def trigger_haptic_feedback(self):
        """Trigger haptic feedback if available"""
        try:
            # Android haptic feedback
            if hasattr(MDApp.get_running_app(), 'vibrate'):
                MDApp.get_running_app().vibrate(0.1)  # 100ms vibration
        except Exception:
            pass  # Haptic feedback not available
    
    def show_ripple_effect(self):
        """Show ripple effect around button"""
        # This would create a visual ripple effect
        # Implementation would depend on the specific UI framework
        pass
    
    def on_touch_down(self, touch):
        """Handle touch down event"""
        if self.collide_point(*touch.pos):
            # Show visual feedback immediately
            self.show_ripple_effect()
            return super().on_touch_down(touch)
        return False
    
    def on_touch_up(self, touch):
        """Handle touch up event"""
        if self.collide_point(*touch.pos):
            return super().on_touch_up(touch)
        return False

class SOSButtonWithHold(SOSButton):
    """SOS button with hold-to-trigger functionality"""
    
    hold_threshold = 2.0  # seconds to hold
    hold_start_time = None
    hold_timer = None
    is_holding = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "Hold for SOS"
    
    def on_touch_down(self, touch):
        """Handle touch down - start hold timer"""
        if self.collide_point(*touch.pos):
            from time import time
            self.hold_start_time = time()
            self.is_holding = True
            
            # Start hold timer
            self.hold_timer = Clock.schedule_once(
                self.on_hold_complete, 
                self.hold_threshold
            )
            
            # Visual feedback for hold start
            self.text = "Holding..."
            self.md_bg_color = (1, 0.2, 0.2, 1)  # Darker red
            
            return super().on_touch_down(touch)
        return False
    
    def on_touch_up(self, touch):
        """Handle touch up - cancel hold if not complete"""
        if self.collide_point(*touch.pos) and self.is_holding:
            self.cancel_hold()
            return super().on_touch_up(touch)
        return False
    
    def on_touch_move(self, touch):
        """Handle touch move - cancel if moved outside button"""
        if self.is_holding and not self.collide_point(*touch.pos):
            self.cancel_hold()
        return super().on_touch_move(touch)
    
    def on_hold_complete(self, dt):
        """Hold threshold reached - trigger SOS"""
        if self.is_holding:
            self.is_holding = False
            self.text = "SOS TRIGGERED"
            self.md_bg_color = COLORS['error']
            
            # Trigger SOS callback
            if hasattr(self, 'on_hold_complete_callback'):
                self.on_hold_complete_callback(self)
    
    def cancel_hold(self):
        """Cancel hold operation"""
        if self.hold_timer:
            self.hold_timer.cancel()
            self.hold_timer = None
        
        self.is_holding = False
        self.text = "Hold for SOS"
        self.md_bg_color = COLORS['error']
    
    def set_hold_threshold(self, seconds: float):
        """Set hold threshold in seconds"""
        self.hold_threshold = max(0.5, min(5.0, seconds))

class MiniSOSButton(SOSButton):
    """Mini SOS button for floating action"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_mini_button()
    
    def setup_mini_button(self):
        """Setup mini button appearance"""
        self.size = (56, 56)  # Standard FAB size
        self.radius = [28, 28, 28, 28]
        self.text = "🆘"  # SOS emoji
        self.font_style = 'H6'
        self.elevation = 6
        
        # Position for floating action button
        self.pos_hint = {'right': 1, 'bottom': 1}
        self.x = -20  # Offset from edge
        self.y = 20
