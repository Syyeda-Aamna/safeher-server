from plyer import accelerometer
from kivy.clock import Clock
from kivy.logger import Logger
import time
import math
from typing import Optional, Callable
from config import SHAKE_THRESHOLD, SHAKE_DURATION, SOS_COOLDOWN_PERIOD

class ShakeService:
    """Shake detection service for SOS trigger"""
    
    def __init__(self):
        self.accelerometer = accelerometer
        self.is_monitoring = False
        self.shake_callbacks = []
        
        # Shake detection variables
        self.shake_start_time = 0
        self.shake_samples = []
        self.last_sos_time = 0
        
        # Accelerometer data
        self.current_accel = {'x': 0, 'y': 0, 'z': 0}
        
    def initialize(self):
        """Initialize accelerometer and start monitoring"""
        try:
            # Enable accelerometer
            self.accelerometer.enable()
            
            # Start monitoring
            self.start_monitoring()
            
            Logger.info("ShakeService: Accelerometer initialized and monitoring started")
            
        except Exception as e:
            Logger.error(f"ShakeService: Error initializing accelerometer: {e}")
    
    def start_monitoring(self):
        """Start shake monitoring"""
        if not self.is_monitoring:
            self.is_monitoring = True
            
            # Schedule accelerometer reading
            Clock.schedule_interval(self.read_accelerometer, 0.1)  # 10 Hz
            
            Logger.info("ShakeService: Shake monitoring started")
    
    def stop_monitoring(self):
        """Stop shake monitoring"""
        if self.is_monitoring:
            self.is_monitoring = False
            
            # Stop accelerometer reading
            Clock.unschedule(self.read_accelerometer)
            
            Logger.info("ShakeService: Shake monitoring stopped")
    
    def read_accelerometer(self, dt):
        """Read accelerometer data and detect shake"""
        try:
            if not self.is_monitoring:
                return
            
            # Get accelerometer data
            accel_data = self.accelerometer.acceleration
            
            if not accel_data or len(accel_data) < 3:
                return
            
            x, y, z = accel_data[:3]
            
            # Calculate magnitude
            magnitude = math.sqrt(x*x + y*y + z*z)
            
            # Store sample
            self.shake_samples.append({
                'magnitude': magnitude,
                'timestamp': time.time()
            })
            
            # Keep only recent samples (last 2 seconds)
            current_time = time.time()
            self.shake_samples = [
                sample for sample in self.shake_samples
                if current_time - sample['timestamp'] < SHAKE_DURATION
            ]
            
            # Detect shake pattern
            self.detect_shake()
            
        except Exception as e:
            Logger.error(f"ShakeService: Error reading accelerometer: {e}")
    
    def detect_shake(self):
        """Detect shake pattern from samples"""
        try:
            if len(self.shake_samples) < 5:
                return
            
            current_time = time.time()
            
            # Check if we have sustained high acceleration
            recent_samples = [
                sample for sample in self.shake_samples
                if current_time - sample['timestamp'] < SHAKE_DURATION
            ]
            
            if len(recent_samples) < 5:
                return
            
            # Calculate average magnitude
            avg_magnitude = sum(sample['magnitude'] for sample in recent_samples) / len(recent_samples)
            
            # Check if average exceeds threshold
            if avg_magnitude > SHAKE_THRESHOLD:
                if self.shake_start_time == 0:
                    self.shake_start_time = current_time
                    Logger.debug(f"ShakeService: Shake detected - magnitude: {avg_magnitude:.2f}")
                
                # Check if shake has been sustained
                if current_time - self.shake_start_time >= SHAKE_DURATION:
                    self.trigger_shake_detected()
                    self.reset_shake_detection()
            
            else:
                # Reset if magnitude drops below threshold
                if self.shake_start_time > 0:
                    self.reset_shake_detection()
                    
        except Exception as e:
            Logger.error(f"ShakeService: Error detecting shake: {e}")
    
    def trigger_shake_detected(self):
        """Trigger shake detected event"""
        try:
            current_time = time.time()
            
            # Check cooldown period
            if current_time - self.last_sos_time < SOS_COOLDOWN_PERIOD:
                Logger.info("ShakeService: SOS in cooldown period")
                return
            
            # Update last SOS time
            self.last_sos_time = current_time
            
            Logger.warning("ShakeService: Shake pattern detected - triggering SOS")
            
            # Notify all callbacks
            for callback in self.shake_callbacks:
                try:
                    callback('shake')
                except Exception as e:
                    Logger.error(f"ShakeService: Error in callback: {e}")
                    
        except Exception as e:
            Logger.error(f"ShakeService: Error triggering shake detected: {e}")
    
    def reset_shake_detection(self):
        """Reset shake detection variables"""
        self.shake_start_time = 0
        self.shake_samples.clear()
    
    def add_shake_callback(self, callback: Callable):
        """Add callback for shake detection"""
        if callback not in self.shake_callbacks:
            self.shake_callbacks.append(callback)
            Logger.info(f"ShakeService: Added shake callback (total: {len(self.shake_callbacks)})")
    
    def remove_shake_callback(self, callback: Callable):
        """Remove shake callback"""
        if callback in self.shake_callbacks:
            self.shake_callbacks.remove(callback)
            Logger.info(f"ShakeService: Removed shake callback (total: {len(self.shake_callbacks)})")
    
    def manual_trigger_test(self):
        """Manual trigger for testing shake detection"""
        Logger.info("ShakeService: Manual trigger test")
        current_time = time.time()
        
        # Check cooldown period
        if current_time - self.last_sos_time < SOS_COOLDOWN_PERIOD:
            Logger.info("ShakeService: Manual trigger blocked by cooldown")
            return False
        
        self.last_sos_time = current_time
        
        # Notify callbacks
        for callback in self.shake_callbacks:
            try:
                callback('manual_test')
            except Exception as e:
                Logger.error(f"ShakeService: Error in manual test callback: {e}")
        
        return True
    
    def get_shake_status(self) -> dict:
        """Get current shake detection status"""
        current_time = time.time()
        
        return {
            'is_monitoring': self.is_monitoring,
            'is_shaking': self.shake_start_time > 0,
            'shake_duration': current_time - self.shake_start_time if self.shake_start_time > 0 else 0,
            'sample_count': len(self.shake_samples),
            'last_sos_time': self.last_sos_time,
            'cooldown_remaining': max(0, SOS_COOLDOWN_PERIOD - (current_time - self.last_sos_time)),
            'accelerometer_enabled': self.accelerometer.is_enabled()
        }
    
    def set_sensitivity(self, threshold: float):
        """Set shake detection sensitivity"""
        global SHAKE_THRESHOLD
        SHAKE_THRESHOLD = max(5.0, min(30.0, threshold))
        Logger.info(f"ShakeService: Sensitivity set to {SHAKE_THRESHOLD}")
    
    def get_current_acceleration(self) -> dict:
        """Get current acceleration values"""
        return self.current_accel.copy()
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.stop_monitoring()
            self.shake_callbacks.clear()
            
            # Disable accelerometer
            if hasattr(self.accelerometer, 'disable'):
                self.accelerometer.disable()
            
            Logger.info("ShakeService: Cleanup completed")
            
        except Exception as e:
            Logger.error(f"ShakeService: Error during cleanup: {e}")
