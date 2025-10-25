"""
CAILculator Auth Server - FastAPI Backend for Railway
Handles API key validation and usage tracking
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
from datetime import datetime
from sqlalchemy.orm import Session
from pathlib import Path

from database import (
    get_db,
    init_db,
    User,
    APIKey,
    UsageLog,
    SubscriptionTier
)

app = FastAPI(
    title="CAILculator Auth Server",
    description="Authentication and usage tracking for CAILculator MCP",
    version="1.0.0"
)

# Templates directory
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class SignupRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class SignupResponse(BaseModel):
    user_id: int
    email: str
    api_key: str
    tier: str
    message: str

class ValidateRequest(BaseModel):
    api_key: str

class ValidateResponse(BaseModel):
    valid: bool
    user_id: Optional[int] = None
    tier: Optional[str] = None
    usage_count: Optional[int] = None
    limit: Optional[int] = None
    message: str

class UsageRequest(BaseModel):
    api_key: str
    tool_name: str
    dimension: Optional[int] = None

# =============================================================================
# SUBSCRIPTION LIMITS
# =============================================================================

TIER_LIMITS = {
    "student": 1_000,      # $4.99/month - 1,000 requests
    "teacher": 5_000,      # $9.99/month - 5,000 requests
    "indie": 15_000,       # $49/month - 15,000 requests
    "team": 100_000,       # $250/month - 100,000 requests
    "enterprise": -1       # $3K+/month - Unlimited
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def check_rate_limit(api_key: str, db: Session) -> tuple[bool, int, int]:
    """
    Check if user has exceeded their rate limit
    Returns: (is_allowed, current_usage, limit)
    """
    # Find API key
    key_record = db.query(APIKey).filter(APIKey.key_hash == api_key).first()
    if not key_record:
        return False, 0, 0

    user = db.query(User).filter(User.id == key_record.user_id).first()
    if not user:
        return False, 0, 0

    # Get limit for tier
    limit = TIER_LIMITS.get(user.tier.value, 100)
    if limit == -1:  # Unlimited
        return True, 0, -1

    # Count usage in last 30 days
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    usage_count = db.query(UsageLog).filter(
        UsageLog.user_id == user.id,
        UsageLog.timestamp >= thirty_days_ago
    ).count()

    return usage_count < limit, usage_count, limit

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Landing page with pricing"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api")
async def api_info():
    """API info endpoint"""
    return {
        "service": "CAILculator Auth Server",
        "status": "operational",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check with database connectivity"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")

@app.post("/signup", response_model=SignupResponse)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Create new user account and generate API key
    Student tier by default (requires payment)
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        email=request.email,
        name=request.name or request.email.split('@')[0],
        tier=SubscriptionTier.STUDENT
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate API key
    import secrets
    api_key = f"cail_{secrets.token_urlsafe(32)}"

    # Store hashed key
    import hashlib
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    api_key_record = APIKey(
        user_id=user.id,
        key_hash=key_hash
    )
    db.add(api_key_record)
    db.commit()

    return SignupResponse(
        user_id=user.id,
        email=user.email,
        api_key=api_key,  # Only time we return plaintext
        tier=user.tier.value,
        message="Account created! Store your API key securely - you won't see it again."
    )

@app.post("/validate", response_model=ValidateResponse)
async def validate(request: ValidateRequest, db: Session = Depends(get_db)):
    """
    Validate API key and check rate limits
    Called by MCP server before each request
    """
    # Hash the provided key
    import hashlib
    key_hash = hashlib.sha256(request.api_key.encode()).hexdigest()

    # Find API key
    key_record = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
    if not key_record:
        return ValidateResponse(
            valid=False,
            message="Invalid API key"
        )

    user = db.query(User).filter(User.id == key_record.user_id).first()
    if not user:
        return ValidateResponse(
            valid=False,
            message="User not found"
        )

    # Check rate limit
    is_allowed, usage_count, limit = check_rate_limit(key_hash, db)

    if not is_allowed:
        return ValidateResponse(
            valid=False,
            user_id=user.id,
            tier=user.tier.value,
            usage_count=usage_count,
            limit=limit,
            message=f"Rate limit exceeded ({usage_count}/{limit} requests this month)"
        )

    return ValidateResponse(
        valid=True,
        user_id=user.id,
        tier=user.tier.value,
        usage_count=usage_count,
        limit=limit,
        message="API key valid"
    )

@app.post("/log-usage")
async def log_usage(request: UsageRequest, db: Session = Depends(get_db)):
    """
    Log API usage for billing and analytics
    Called by MCP server after successful request
    """
    # Hash the provided key
    import hashlib
    key_hash = hashlib.sha256(request.api_key.encode()).hexdigest()

    # Find API key
    key_record = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
    if not key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Log usage
    usage = UsageLog(
        user_id=key_record.user_id,
        tool_name=request.tool_name,
        dimension=request.dimension
    )
    db.add(usage)
    db.commit()

    return {"status": "logged"}

@app.get("/usage/{api_key}")
async def get_usage(api_key: str, db: Session = Depends(get_db)):
    """
    Get usage statistics for an API key
    """
    # Hash the provided key
    import hashlib
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    # Find API key
    key_record = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
    if not key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")

    user = db.query(User).filter(User.id == key_record.user_id).first()

    # Count usage in last 30 days
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    usage_count = db.query(UsageLog).filter(
        UsageLog.user_id == user.id,
        UsageLog.timestamp >= thirty_days_ago
    ).count()

    limit = TIER_LIMITS.get(user.tier.value, 100)

    return {
        "user_id": user.id,
        "email": user.email,
        "tier": user.tier.value,
        "usage_30_days": usage_count,
        "limit": limit if limit != -1 else "unlimited",
        "remaining": (limit - usage_count) if limit != -1 else "unlimited"
    }

# =============================================================================
# STARTUP/SHUTDOWN
# =============================================================================

@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    print("Starting CAILculator Auth Server...")
    init_db()
    print("Database initialized!")
    print("Server ready!")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    print("Shutting down CAILculator Auth Server...")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
