"""
CAILculator Auth Server - FastAPI Backend for Railway
Handles API key validation and usage tracking
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from pathlib import Path
import stripe
import secrets
import hashlib
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from database import (
    get_db,
    init_db,
    User,
    APIKey,
    UsageLog,
    SubscriptionTier,
    SignupAttempt
)

app = FastAPI(
    title="CAILculator Auth Server",
    description="Authentication and usage tracking for CAILculator MCP",
    version="1.0.0"
)

# Templates and static files directory
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Create static directory if it doesn't exist (for Railway deployment)
static_dir = BASE_DIR / "static"
static_dir.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Stripe Price IDs (LIVE MODE - Production)
STRIPE_PRICES = {
    "indie": "price_1SMvzF2NNm10BnLCEPbug1yj",        # $19/month - 5,000 requests
    "academic": "price_1SMvz42NNm10BnLCM3HNLmg0",     # $99/month - 25,000 requests
    "professional": "price_1SMvyr2NNm10BnLCJowLJz7d"  # $299/month - 100,000 requests
    # Free tier doesn't need Stripe
    # Enterprise is custom pricing (contact sales)
}

# SendGrid configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "iknowpi@gmail.com")

# Auto-approved countries (US, Canada, EU, UK, Australia, Japan, New Zealand)
AUTO_APPROVED_COUNTRIES = {
    "US", "CA",  # North America
    "GB", "IE",  # UK & Ireland
    "AU", "NZ",  # Oceania
    "JP", "KR", "SG",  # Asia (friendly)
    # EU countries
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
    "DE", "GR", "HU", "IT", "LV", "LT", "LU", "MT", "NL", "PL",
    "PT", "RO", "SK", "SI", "ES", "SE", "NO", "CH", "IS"
}

# IP rate limiting: max signups per IP per day
MAX_SIGNUPS_PER_IP_PER_DAY = 3

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
    "free": 100,            # $0/month - 100 requests
    "indie": 5_000,         # $19/month - 5,000 requests
    "academic": 25_000,     # $99/month - 25,000 requests
    "professional": 100_000,# $299/month - 100,000 requests
    "enterprise": -1        # Custom pricing - Unlimited
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    # Check for Railway/proxy forwarded IP first
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fallback to direct connection
    if request.client:
        return request.client.host

    return "unknown"

def get_country_from_ip(ip_address: str) -> Optional[str]:
    """
    Get country code from IP address using free ipapi.co service
    Returns 2-letter ISO country code or None
    """
    if ip_address == "unknown" or ip_address.startswith("127.") or ip_address.startswith("192.168."):
        return "US"  # Default for localhost/development

    try:
        response = requests.get(f"https://ipapi.co/{ip_address}/country/", timeout=2)
        if response.status_code == 200:
            country_code = response.text.strip()
            return country_code if len(country_code) == 2 else None
    except:
        pass

    return None

def check_ip_rate_limit(ip_address: str, db: Session) -> tuple[bool, int]:
    """
    Check if IP has exceeded signup rate limit
    Returns: (is_allowed, signup_count_today)
    """
    # Count signups from this IP in last 24 hours
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)

    signup_count = db.query(SignupAttempt).filter(
        SignupAttempt.ip_address == ip_address,
        SignupAttempt.timestamp >= twenty_four_hours_ago
    ).count()

    is_allowed = signup_count < MAX_SIGNUPS_PER_IP_PER_DAY
    return is_allowed, signup_count

def send_verification_email(email: str, verification_token: str, base_url: str) -> bool:
    """
    Send email verification link using SendGrid
    Returns True if successful, False otherwise
    """
    if not SENDGRID_API_KEY:
        print("WARNING: SENDGRID_API_KEY not set, skipping email")
        return False

    verification_url = f"{base_url}/verify-email?token={verification_token}"

    message = Mail(
        from_email=SENDGRID_FROM_EMAIL,
        to_emails=email,
        subject="Verify your CAILculator MCP account",
        html_content=f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #667eea;">CAILculator MCP</h1>
                    <p style="color: #666; font-style: italic;">"Better math, less suffering"</p>
                </div>

                <h2>Welcome to CAILculator MCP!</h2>

                <p>Thank you for signing up. You're one step away from accessing high-dimensional mathematical analysis tools.</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}"
                       style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                              color: white;
                              padding: 15px 40px;
                              text-decoration: none;
                              border-radius: 5px;
                              display: inline-block;
                              font-weight: bold;">
                        Verify Email Address
                    </a>
                </div>

                <p style="color: #666; font-size: 0.9em;">
                    This link will expire in 24 hours. If you didn't create this account, you can safely ignore this email.
                </p>

                <p style="color: #666; font-size: 0.9em; margin-top: 30px;">
                    Or copy and paste this URL into your browser:<br>
                    <a href="{verification_url}" style="color: #667eea;">{verification_url}</a>
                </p>

                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">

                <p style="color: #999; font-size: 0.85em; text-align: center;">
                    <strong>Chavez AI Labs</strong><br>
                    Research tools for high-dimensional mathematics<br>
                    <a href="mailto:iknowpi@gmail.com" style="color: #667eea;">iknowpi@gmail.com</a>
                </p>
            </div>
        </body>
        </html>
        """
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Verification email sent to {email}: Status {response.status_code}")
        return response.status_code in [200, 202]
    except Exception as e:
        print(f"Failed to send email to {email}: {str(e)}")
        return False

def send_api_key_email(email: str, api_key: str, tier: str) -> bool:
    """
    Send API key to user after paid subscription or manual approval
    Returns True if successful, False otherwise
    """
    if not SENDGRID_API_KEY:
        print("WARNING: SENDGRID_API_KEY not set, skipping email")
        return False

    tier_info = {
        "free": {"limit": "100 requests/month", "price": "Free"},
        "indie": {"limit": "5,000 requests/month", "price": "$19/month"},
        "academic": {"limit": "25,000 requests/month", "price": "$99/month"},
        "professional": {"limit": "100,000 requests/month", "price": "$299/month"},
        "enterprise": {"limit": "Unlimited", "price": "Custom pricing"}
    }

    tier_details = tier_info.get(tier, {"limit": "Unknown", "price": "Unknown"})

    message = Mail(
        from_email=SENDGRID_FROM_EMAIL,
        to_emails=email,
        subject="Your CAILculator MCP API Key",
        html_content=f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #667eea;">CAILculator MCP</h1>
                    <p style="color: #666; font-style: italic;">"Better math, less suffering"</p>
                </div>

                <h2>Your API Key is Ready!</h2>

                <p>Welcome to CAILculator MCP! Your account has been approved and your API key is ready to use.</p>

                <div style="background-color: #f7fafc; border-left: 4px solid #667eea; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: bold; color: #667eea;">Your Subscription Details:</p>
                    <p style="margin: 5px 0;"><strong>Tier:</strong> {tier.capitalize()}</p>
                    <p style="margin: 5px 0;"><strong>Price:</strong> {tier_details['price']}</p>
                    <p style="margin: 5px 0;"><strong>Usage Limit:</strong> {tier_details['limit']}</p>
                </div>

                <div style="background-color: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 5px; margin: 20px 0; font-family: monospace; word-break: break-all;">
                    <p style="margin: 0; font-size: 0.9em;"><strong>API Key:</strong></p>
                    <p style="margin: 5px 0; font-size: 1em;">{api_key}</p>
                </div>

                <div style="background-color: #fff5f5; border-left: 4px solid #f56565; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #c53030;"><strong>⚠️ Important:</strong> Keep this API key secure! It's like a password for your account.</p>
                </div>

                <h3>Getting Started</h3>
                <ol style="line-height: 1.8;">
                    <li>Copy your API key above</li>
                    <li>Add it to your Claude Desktop configuration</li>
                    <li>Restart Claude Desktop</li>
                    <li>Start exploring zero divisors in high-dimensional algebras!</li>
                </ol>

                <p>For setup instructions and documentation, visit: <a href="https://github.com/pchavez2029/CAILculator" style="color: #667eea;">github.com/pchavez2029/CAILculator</a></p>

                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">

                <p style="color: #999; font-size: 0.85em; text-align: center;">
                    <strong>Chavez AI Labs</strong><br>
                    Research tools for high-dimensional mathematics<br>
                    Questions? Reply to this email or contact <a href="mailto:iknowpi@gmail.com" style="color: #667eea;">iknowpi@gmail.com</a>
                </p>
            </div>
        </body>
        </html>
        """
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"API key email sent to {email}: Status {response.status_code}")
        return response.status_code in [200, 202]
    except Exception as e:
        print(f"Failed to send API key email to {email}: {str(e)}")
        return False

def send_manual_approval_pending_email(email: str, country_code: str) -> bool:
    """
    Notify user that their signup requires manual approval
    Returns True if successful, False otherwise
    """
    if not SENDGRID_API_KEY:
        print("WARNING: SENDGRID_API_KEY not set, skipping email")
        return False

    message = Mail(
        from_email=SENDGRID_FROM_EMAIL,
        to_emails=email,
        subject="CAILculator MCP - Manual Approval Required",
        html_content=f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #667eea;">CAILculator MCP</h1>
                    <p style="color: #666; font-style: italic;">"Better math, less suffering"</p>
                </div>

                <h2>Email Verified - Approval Pending</h2>

                <p>Thank you for verifying your email address! Your signup from <strong>{country_code or 'your region'}</strong> requires manual approval as part of our security process.</p>

                <div style="background-color: #f7fafc; border-left: 4px solid #667eea; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: bold; color: #667eea;">What happens next?</p>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>Our team will review your signup within 24 hours</li>
                        <li>You'll receive your API key via email once approved</li>
                        <li>No action required from you - just sit tight!</li>
                    </ul>
                </div>

                <div style="background-color: #fffaf0; border-left: 4px solid #ed8936; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #7c2d12;"><strong>Why manual approval?</strong></p>
                    <p style="margin: 10px 0 0 0; color: #7c2d12;">We review signups from certain regions to prevent abuse and maintain service quality for legitimate researchers and developers.</p>
                </div>

                <p>We appreciate your patience and look forward to having you explore high-dimensional mathematics with CAILculator MCP!</p>

                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">

                <p style="color: #999; font-size: 0.85em; text-align: center;">
                    <strong>Chavez AI Labs</strong><br>
                    Research tools for high-dimensional mathematics<br>
                    Questions? Reply to this email or contact <a href="mailto:iknowpi@gmail.com" style="color: #667eea;">iknowpi@gmail.com</a>
                </p>
            </div>
        </body>
        </html>
        """
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Manual approval notification sent to {email}: Status {response.status_code}")
        return response.status_code in [200, 202]
    except Exception as e:
        print(f"Failed to send manual approval email to {email}: {str(e)}")
        return False

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

@app.post("/signup")
async def signup(signup_request: SignupRequest, request: Request, db: Session = Depends(get_db)):
    """
    Create new user account and send verification email
    API key generated after email verification
    """
    # Get client IP
    client_ip = get_client_ip(request)

    # Check IP rate limit
    is_allowed, signup_count = check_ip_rate_limit(client_ip, db)
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Too many signup attempts from your IP address. Limit: {MAX_SIGNUPS_PER_IP_PER_DAY} per day."
        )

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == signup_request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Get country from IP
    country_code = get_country_from_ip(client_ip)

    # Check if auto-approved or requires manual approval
    requires_manual = (country_code not in AUTO_APPROVED_COUNTRIES) if country_code else True

    # Generate verification token
    verification_token = secrets.token_urlsafe(32)
    token_expires = datetime.utcnow() + timedelta(hours=24)

    # Create user (WITHOUT API key yet)
    user = User(
        email=signup_request.email,
        name=signup_request.name or signup_request.email.split('@')[0],
        tier=SubscriptionTier.FREE,
        email_verified=0,
        verification_token=verification_token,
        verification_token_expires=token_expires,
        country_code=country_code,
        signup_ip=client_ip,
        requires_manual_approval=1 if requires_manual else 0
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Log signup attempt
    signup_attempt = SignupAttempt(
        ip_address=client_ip,
        success=1
    )
    db.add(signup_attempt)
    db.commit()

    # Get base URL
    base_url = os.getenv("RAILWAY_PUBLIC_DOMAIN", request.base_url)
    if isinstance(base_url, str) and not base_url.startswith("http"):
        base_url = f"https://{base_url}"
    else:
        base_url = str(base_url).rstrip("/")

    # Send verification email
    email_sent = send_verification_email(signup_request.email, verification_token, base_url)

    if not email_sent:
        # Email failed but user created - they can resend later
        print(f"WARNING: Failed to send verification email to {signup_request.email}")

    response_message = "Account created! Please check your email to verify your account."
    if requires_manual:
        response_message += f" Note: Signups from {country_code or 'your region'} require manual approval. You will receive your API key within 24 hours of approval."

    return {
        "message": response_message,
        "email": signup_request.email,
        "requires_manual_approval": requires_manual,
        "email_sent": email_sent
    }

@app.get("/signup-free", response_class=HTMLResponse)
async def signup_free_page(request: Request):
    """
    Free tier signup page (simple email form)
    """
    return templates.TemplateResponse("signup_free.html", {"request": request})

@app.get("/verify-email", response_class=HTMLResponse)
async def verify_email(request: Request, token: str, db: Session = Depends(get_db)):
    """
    Verify email address and generate API key
    """
    # Find user by verification token
    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        return templates.TemplateResponse("verification_result.html", {
            "request": request,
            "success": False,
            "message": "Invalid verification link. The token may have expired or already been used."
        })

    # Check if token expired
    if user.verification_token_expires and user.verification_token_expires < datetime.utcnow():
        return templates.TemplateResponse("verification_result.html", {
            "request": request,
            "success": False,
            "message": "Verification link has expired. Please sign up again."
        })

    # Check if already verified
    if user.email_verified == 1:
        # Find existing API key
        existing_key = db.query(APIKey).filter(APIKey.user_id == user.id).first()
        if existing_key:
            return templates.TemplateResponse("verification_result.html", {
                "request": request,
                "success": True,
                "message": "Email already verified. Your API key was sent previously.",
                "already_verified": True
            })

    # Check if requires manual approval
    if user.requires_manual_approval == 1:
        user.email_verified = 1
        user.verification_token = None
        db.commit()

        # Send manual approval notification email
        send_manual_approval_pending_email(user.email, user.country_code)

        return templates.TemplateResponse("verification_result.html", {
            "request": request,
            "success": True,
            "message": f"Email verified! Your signup from {user.country_code or 'your region'} requires manual approval. You will receive your API key within 24 hours.",
            "requires_approval": True
        })

    # Generate API key
    api_key_plain = f"cail_{secrets.token_urlsafe(32)}"
    api_key_hash = hashlib.sha256(api_key_plain.encode()).hexdigest()

    # Mark as verified
    user.email_verified = 1
    user.verification_token = None

    # Create API key record
    api_key_record = APIKey(
        user_id=user.id,
        key_hash=api_key_hash
    )
    db.add(api_key_record)
    db.commit()

    return templates.TemplateResponse("verification_result.html", {
        "request": request,
        "success": True,
        "api_key": api_key_plain,
        "email": user.email,
        "tier": user.tier.value,
        "message": "Email verified successfully! Your API key is ready."
    })

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

# =============================================================================
# STRIPE CHECKOUT
# =============================================================================

@app.get("/create-checkout-session")
async def create_checkout_session(tier: str):
    """
    Create Stripe checkout session for subscription
    """
    if tier not in STRIPE_PRICES:
        raise HTTPException(status_code=400, detail="Invalid subscription tier")

    try:
        # Get the base URL (Railway sets this automatically)
        base_url = os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost:8000")
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': STRIPE_PRICES[tier],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{base_url}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/?canceled=true",
            metadata={
                'tier': tier
            }
        )

        return RedirectResponse(url=checkout_session.url, status_code=303)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/success")
async def success(request: Request, session_id: str):
    """
    Success page after checkout
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)

        return templates.TemplateResponse("success.html", {
            "request": request,
            "session": session
        })
    except Exception as e:
        return templates.TemplateResponse("success.html", {
            "request": request,
            "error": str(e)
        })

@app.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhooks for subscription events
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    # For now, just log the event (we'll add webhook secret later)
    try:
        import json
        event = stripe.Event.construct_from(
            json.loads(payload.decode('utf-8')), stripe.api_key
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Handle successful subscription creation
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Get customer email and tier from session
        customer_email = session.get('customer_email') or session.get('customer_details', {}).get('email')
        tier = session.get('metadata', {}).get('tier', 'student')

        if customer_email:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == customer_email).first()

            if not existing_user:
                # Create user
                user = User(
                    email=customer_email,
                    name=customer_email.split('@')[0],
                    tier=SubscriptionTier(tier)
                )
                db.add(user)
                db.commit()
                db.refresh(user)

                # Generate API key
                api_key_plain = f"cail_{secrets.token_urlsafe(32)}"
                api_key_hash = hashlib.sha256(api_key_plain.encode()).hexdigest()

                api_key_record = APIKey(
                    user_id=user.id,
                    key_hash=api_key_hash
                )
                db.add(api_key_record)
                db.commit()

                # Send API key via email
                send_api_key_email(customer_email, api_key_plain, tier)
                print(f"Created user {customer_email} with API key: {api_key_plain}")

    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
