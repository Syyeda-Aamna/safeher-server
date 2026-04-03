from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
from config import settings
from services.db import init_db
from services.scheduler import start_scheduler
from routes import auth, contacts, sos, location, checkin, incidents, police

security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    start_scheduler()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="SafeHer API",
    description="Women Safety Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all route modules
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(contacts.router, prefix="/api/contacts", tags=["Emergency Contacts"])
app.include_router(sos.router, prefix="/api/sos", tags=["SOS Alerts"])
app.include_router(location.router, prefix="/api/location", tags=["Location Services"])
app.include_router(checkin.router, prefix="/api/checkin", tags=["Check-in Timer"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["Incident Reports"])
app.include_router(police.router, prefix="/api/police", tags=["Police Stations"])

@app.get("/")
async def root():
    return {"message": "SafeHer API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "SafeHer API"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
