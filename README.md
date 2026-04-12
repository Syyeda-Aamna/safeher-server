# SafeHer - Women Safety Platform

A complete, production-ready women safety platform with real-time SOS alerts, location sharing, and emergency contacts management.

##   Features

###  Mobile App Features
- **One-Tap SOS**: Instant emergency alerts to all contacts
- **Shake-to-SOS**: Trigger SOS by shaking phone vigorously
- **Real GPS Tracking**: Live location sharing with emergency contacts
- **Check-in Timer**: Automatic alerts if you don't check in safely
- **Emergency Contacts**: Add unlimited family/friends contacts
- **Police Stations**: Find nearby police stations with directions
- **Incident Reporting**: Document and report safety incidents
- **Offline Mode**: Works without internet using native SMS
- **Beautiful UI**: Modern dark theme with glassmorphism design

### Server Features
- **FastAPI Backend**: High-performance REST API
- **MongoDB Database**: Scalable cloud database
- **Real SMS Alerts**: Fast2SMS integration for Indian numbers
- **JWT Authentication**: Secure user authentication
- **Location Services**: Google Maps integration
- **Background Tasks**: Automated check-in monitoring
- **Multi-User Support**: Thousands of women can use simultaneously

##  Architecture

```
SafeHer Platform
├── Backend Server (Python/FastAPI)
│   ├── MongoDB Atlas Database
│   ├── Fast2SMS Service
│   ├── Google Maps API
│   └── JWT Authentication
└── Mobile App (Python/Kivy)
    ├── Local SQLite Database
    ├── GPS & Accelerometer
    ├── Native SMS Integration
    └── Beautiful Material UI
```

##  Quick Start

### Prerequisites
- Python 3.11+
- MongoDB Atlas account
- Fast2SMS account
- Google Maps API key
- Android device (for testing)

### 1. Server Setup

#### Clone Repository
```bash
git clone <repository-url>
cd safeher-server
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

#### Required Environment Variables
- `MONGO_URI`: MongoDB Atlas connection string
- `JWT_SECRET`: Strong random secret for JWT tokens
- `FAST2SMS_API_KEY`: Fast2SMS API key
- `GOOGLE_MAPS_KEY`: Google Maps API key

#### Run Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Mobile App Setup

#### Clone Repository
```bash
cd ../safeher-app
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Build APK
```bash
buildozer android debug
```

#### Install on Android
```bash
# Transfer APK to phone
adb install bin/safeher-1.0.0-debug.apk
```

## Detailed Setup Instructions

### MongoDB Atlas Setup

1. **Create Account**
   - Go to [MongoDB Atlas](https://cloud.mongodb.com/)
   - Sign up for free account (no credit card required)

2. **Create Cluster**
   - Click "Build a Cluster"
   - Select M0 Free Tier
   - Choose cloud provider and region (recommended: AWS, Mumbai)

3. **Create Database User**
   - Go to Database Access → Add New Database User
   - Enter username and strong password
   - Save credentials securely

4. **Get Connection String**
   - Go to Database → Connect → Connect your application
   - Select "Python" driver
   - Copy connection string
   - Replace `<password>` with actual password

5. **Update Environment**
   ```env
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/safeher
   ```

### Fast2SMS Setup

1. **Create Account**
   - Go to [Fast2SMS](https://www.fast2sms.com/)
   - Sign up for free account

2. **Get API Key**
   - Go to Dashboard → Dev API
   - Copy your API key
   - Note: Free tier provides sufficient credits for testing

3. **Update Environment**
   ```env
   FAST2SMS_API_KEY=your_api_key_here
   ```

### Google Maps API Setup

1. **Create Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project: "SafeHer"

2. **Enable APIs**
   - Go to APIs & Services → Library
   - Enable these APIs:
     - Maps JavaScript API
     - Places API
     - Geocoding API
     - Directions API

3. **Create API Key**
   - Go to Credentials → Create Credentials → API Key
   - Restrict key to HTTP referrers for security
   - Copy API key

4. **Update Environment**
   ```env
   GOOGLE_MAPS_KEY=your_google_maps_key_here
   ```

### Security Setup

1. **Generate JWT Secret**
   ```bash
   openssl rand -base64 32
   ```

2. **Update Environment**
   ```env
   JWT_SECRET=your_generated_secret_here
   ```

## Deployment

### Deploy Server to Render.com

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial SafeHer deployment"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [Render.com](https://render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select branch: `main`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables**
   - Go to Service → Environment
   - Add all variables from `.env` file
   - **Never commit `.env` to version control**

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (2-3 minutes)
   - Your API will be available at: `https://your-app-name.onrender.com`

### Update Mobile App Configuration

1. **Edit Config**
   ```python
   # safeher-app/config.py
   SERVER_URL = "https://your-app-name.onrender.com"
   ```

2. **Rebuild APK**
   ```bash
   buildozer android debug
   ```

## Testing

### Test Server API

```bash
# Health check
curl https://your-app.onrender.com/health

# Register user
curl -X POST https://your-app.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "phone": "9876543210",
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

### Test Mobile App

1. **Install APK**
   - Transfer `safeher-1.0.0-debug.apk` to Android phone
   - Enable "Install from unknown sources" in settings
   - Install and open app

2. **Create Account**
   - Open SafeHer app
   - Click "Create Account"
   - Enter details and verify OTP

3. **Add Emergency Contacts**
   - Go to Contacts screen
   - Add 2-3 family/friends contacts

4. **Test SOS**
   - Go to Dashboard
   - Hold SOS button for 2 seconds
   - Check if contacts receive SMS alerts

## Development

### Server Development

```bash
cd safeher-server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Mobile Development

```bash
cd safeher-app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## API Documentation

Once deployed, visit:
- Swagger UI: `https://your-app.onrender.com/docs`
- ReDoc: `https://your-app.onrender.com/redoc`

### Key Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/verify-otp` - Verify phone number
- `POST /api/auth/login` - User login
- `POST /api/auth/request-otp` - Request password reset

#### Emergency Contacts
- `GET /api/contacts` - Get user's contacts
- `POST /api/contacts` - Add new contact
- `PUT /api/contacts/{id}` - Update contact
- `DELETE /api/contacts/{id}` - Delete contact

#### SOS Alerts
- `POST /api/sos/trigger` - Trigger SOS alert
- `POST /api/sos/cancel` - Cancel active SOS
- `GET /api/sos/history` - Get SOS history

#### Location Services
- `POST /api/location/update` - Update GPS location
- `POST /api/location/share` - Create location share
- `GET /api/location/live/{token}` - Public live location

## Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt with 12 rounds
- **OTP Rate Limiting**: 5 OTPs per hour per phone
- **Input Validation**: Pydantic models for all inputs
- **CORS Protection**: Configured for mobile app
- **Environment Variables**: Sensitive data never in code

## Scaling

### Free Tier Limitations
- **Render.com**: 750 hours/month, 512MB RAM
- **MongoDB Atlas**: 512MB storage
- **Fast2SMS**: Limited SMS credits
- **Google Maps**: $200/month free credit

### Production Scaling
- Upgrade to paid tiers as needed
- Use Redis for session storage
- Implement SMS provider fallbacks
- Add CDN for static assets

## Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check environment variables
print(os.getenv('MONGO_URI'))

# Test MongoDB connection
python -c "from services.db import Database; Database.connect()"
```

#### SMS Not Working
- Verify Fast2SMS API key
- Check phone number format (10-digit Indian)
- Check Fast2SMS account balance

#### Mobile App Crashes
- Enable USB debugging on Android
- Check logs: `adb logcat`
- Verify all permissions granted

#### GPS Not Working
- Enable location services on phone
- Grant location permission to app
- Test outdoors with clear sky view

### Debug Mode

```bash
# Server debug
export DEBUG=True
uvicorn main:app --reload

# Mobile debug
export SAFEHER_DEBUG=True
python main.py
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue in the repository
- Email: support@safeher.app
- Documentation: [Wiki](wiki-link)

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [Kivy](https://kivy.org/) - Mobile app framework
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) - Database hosting
- [Fast2SMS](https://www.fast2sms.com/) - SMS service
- [Google Maps](https://developers.google.com/maps) - Location services

---

** Important**: This is a real safety application. Test thoroughly before deployment. Ensure all emergency features work correctly before relying on them in real situations.

**🛡️ Made with ❤️ for women's safety in India**
