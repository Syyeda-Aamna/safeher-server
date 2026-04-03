import os

# App Configuration
APP_NAME = "SafeHer"
APP_VERSION = "1.0.0"
APP_PACKAGE = "com.safeher.app"

# Server Configuration
SERVER_URL = "https://safeher-api.onrender.com"
API_BASE_URL = f"{SERVER_URL}/api"

# API Endpoints
ENDPOINTS = {
    "auth": {
        "register": "/auth/register",
        "verify_otp": "/auth/verify-otp",
        "login": "/auth/login",
        "request_otp": "/auth/request-otp",
        "reset_password": "/auth/reset-password",
        "me": "/auth/me"
    },
    "contacts": {
        "list": "/contacts",
        "create": "/contacts",
        "update": "/contacts/{}",
        "delete": "/contacts/{}",
        "primary": "/contacts/primary/summary"
    },
    "sos": {
        "trigger": "/sos/trigger",
        "cancel": "/sos/cancel",
        "status": "/sos/status",
        "history": "/sos/history",
        "active_count": "/sos/active/count"
    },
    "location": {
        "update": "/location/update",
        "current": "/location/current",
        "share": "/location/share",
        "shares": "/location/shares",
        "delete_share": "/location/shares/{}",
        "live": "/location/live/{}",
        "cleanup": "/location/cleanup"
    },
    "checkin": {
        "start": "/checkin/start",
        "safe": "/checkin/safe",
        "status": "/checkin/status",
        "history": "/checkin/history",
        "monitor": "/checkin/monitor",
        "cancel": "/checkin/cancel/{}"
    },
    "incidents": {
        "list": "/incidents",
        "create": "/incidents",
        "get": "/incidents/{}",
        "update": "/incidents/{}",
        "delete": "/incidents/{}",
        "sync": "/incidents/{}/sync",
        "stats": "/incidents/stats/summary"
    },
    "police": {
        "nearby": "/police/nearby",
        "helplines": "/police/helplines",
        "station": "/police/station/{}",
        "directions": "/police/directions"
    }
}

# Database Configuration
DATABASE_NAME = "safeher_local.db"

# Location Configuration
LOCATION_UPDATE_INTERVAL = 60  # seconds
GPS_ACCURACY_THRESHOLD = 100  # meters

# SOS Configuration
SOS_COOLDOWN_PERIOD = 30  # seconds
SHAKE_THRESHOLD = 15.0  # m/s²
SHAKE_DURATION = 2.0  # seconds

# UI Configuration
SCREEN_TIMEOUT = 300  # seconds
ANIMATION_DURATION = 0.3  # seconds

# Notification Configuration
NOTIFICATION_CHANNEL_ID = "safeher_notifications"
NOTIFICATION_CHANNEL_NAME = "SafeHer Safety Alerts"

# Emergency Helplines
EMERGENCY_HELPLINES = [
    {"name": "Police", "number": "100", "category": "emergency"},
    {"name": "Women Helpline", "number": "1091", "category": "women_safety"},
    {"name": "Domestic Abuse", "number": "181", "category": "women_safety"},
    {"name": "Ambulance", "number": "102", "category": "medical"},
    {"name": "Fire Brigade", "number": "101", "category": "emergency"},
    {"name": "National Emergency", "number": "112", "category": "emergency"}
]

# Safety Tips
SAFETY_TIPS = [
    {
        "title": "Trust Your Instincts",
        "content": "If a situation feels wrong, it probably is. Remove yourself immediately and don't worry about being polite.",
        "category": "awareness"
    },
    {
        "title": "Stay Alert",
        "content": "Avoid distractions like headphones or phone use while walking alone, especially in unfamiliar areas.",
        "category": "prevention"
    },
    {
        "title": "Share Your Location",
        "content": "Always let someone know where you're going and when you expect to arrive. Use our location sharing feature.",
        "category": "planning"
    },
    {
        "title": "Emergency Contacts",
        "content": "Keep your emergency contacts updated and make sure they know how to respond to SOS alerts.",
        "category": "preparation"
    },
    {
        "title": "Self-Defense Basics",
        "content": "Learn basic self-defense techniques. Your voice, keys, or phone can be used as improvised weapons.",
        "category": "response"
    },
    {
        "title": "Safe Routes",
        "content": "Plan your routes in advance and stick to well-lit, populated areas, especially at night.",
        "category": "planning"
    }
]

# Colors (Theme)
COLORS = {
    "primary": "#C2185B",
    "secondary": "#7B1FA2", 
    "accent": "#FF4081",
    "background": "#0D0D1A",
    "surface": "#1A1A2E",
    "surface_variant": "#16213E",
    "success": "#00E676",
    "warning": "#FFD740",
    "error": "#FF1744",
    "text_primary": "#FFFFFF",
    "text_secondary": "#B0BEC5",
    "border": "rgba(255,255,255,0.08)"
}

# Permissions Required
REQUIRED_PERMISSIONS = [
    "android.permission.INTERNET",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.ACCESS_BACKGROUND_LOCATION",
    "android.permission.SEND_SMS",
    "android.permission.CALL_PHONE",
    "android.permission.READ_PHONE_STATE",
    "android.permission.VIBRATE",
    "android.permission.RECEIVE_BOOT_COMPLETED",
    "android.permission.FOREGROUND_SERVICE",
    "android.permission.CAMERA",
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.WRITE_EXTERNAL_STORAGE"
]

# Feature Flags
FEATURES = {
    "shake_to_sos": True,
    "background_location": True,
    "voice_commands": False,
    "offline_mode": True,
    "auto_emergency_call": False
}

# Development Settings
DEBUG = os.getenv("SAFEHER_DEBUG", "False").lower() == "true"
LOG_LEVEL = "DEBUG" if DEBUG else "INFO"

# Cache Settings
CACHE_DURATION = 3600  # seconds
MAX_CACHE_SIZE = 100  # items

# Network Settings
REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
