import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # MongoDB Configuration
    MONGO_URI: str = os.getenv("MONGO_URI")
    
    # Fast2SMS Configuration
    FAST2SMS_API_KEY: str = os.getenv("FAST2SMS_API_KEY")
    FAST2SMS_BASE_URL: str = "https://www.fast2sms.com/dev/bulkV2"
    
    # Google Maps Configuration
    GOOGLE_MAPS_KEY: str = os.getenv("GOOGLE_MAPS_KEY")
    GOOGLE_MAPS_PLACES_URL: str = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    GOOGLE_MAPS_GEOCODE_URL: str = "https://maps.googleapis.com/maps/api/geocode/json"
    
    # JWT Configuration
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days
    JWT_REFRESH_EXPIRE_MINUTES: int = 90 * 24 * 60  # 90 days
    
    # OTP Configuration
    OTP_EXPIRY_MINUTES: int = 10
    MAX_OTP_PER_HOUR: int = 5
    OTP_LENGTH: int = 6
    
    # Application Configuration
    APP_NAME: str = "SafeHer"
    APP_VERSION: str = "1.0.0"
    
    # Security Configuration
    BCRYPT_ROUNDS: int = 12
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Location Configuration
    LOCATION_UPDATE_INTERVAL_MINUTES: int = 60
    
    # Check-in Configuration
    CHECKIN_TIMER_MAX_HOURS: int = 24
    
    # SMS Templates
    OTP_MESSAGE_TEMPLATE: str = "Your SafeHer OTP is {otp}. Valid for 10 minutes. Do not share this with anyone."
    SOS_MESSAGE_TEMPLATE: str = "EMERGENCY ALERT from {user_name}! She needs help NOW. Location: https://maps.google.com/?q={lat},{lon} | Address: {address} | Time: {time}. Please call her or reach this location immediately. - SafeHer App"
    CHECKIN_MISSED_MESSAGE_TEMPLATE: str = "ALERT: {user_name} has NOT checked in safe by {deadline}. Last location: https://maps.google.com/?q={lat},{lon}. Please check on her immediately. - SafeHer App"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()
