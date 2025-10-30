"""
Stripe Webhook Handler for CAILculator Auth Server
Handles subscription events and generates API keys

Deploy this to Railway alongside your auth server
"""

from flask import Flask, request, jsonify
import stripe
import os
import secrets
import string
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import database functions
from database import store_api_key, deactivate_subscription

app = Flask(__name__)

# Configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Email configuration (for sending API keys via SendGrid)
SMTP_HOST = "smtp.sendgrid.net"
SMTP_PORT = 587
SMTP_USER = "apikey"  # SendGrid uses literal string "apikey" as username
SMTP_PASSWORD = os.getenv("SENDGRID_API_KEY")  # Your SendGrid API key
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "iknowpi@gmail.com")


def generate_api_key(tier: str) -> str:
    """
    Generate a secure API key with tier prefix

    Format: cail_{tier}_{random}
    Example: cail_individual_8Kx9mN2pQ5rL3wY7
    """
    # 20 character random string (alphanumeric)
    random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
    return f"cail_{tier}_{random_part}"


def send_api_key_email(email: str, api_key: str, tier: str, customer_name: str = None):
    """
    Send API key to customer via email
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"⚠️  Email not configured - API key: {api_key}")
        return

    subject = "Your CAILculator API Key"

    # Friendly tier names
    tier_names = {
        "individual": "Individual",
        "academic": "Academic",
        "commercial": "Commercial"
    }
    tier_display = tier_names.get(tier, tier.title())

    # Email body
    body = f"""
Hello{f' {customer_name}' if customer_name else ''},

Thank you for subscribing to CAILculator {tier_display}!

Your API key is ready:

    {api_key}

To get started:

1. Install Claude Desktop (if you haven't already)
2. Add CAILculator to your MCP configuration:

   Windows: %APPDATA%\\Claude\\claude_desktop_config.json
   Mac/Linux: ~/Library/Application Support/Claude/claude_desktop_config.json

3. Add this configuration:

{{
  "mcpServers": {{
    "cailculator-mcp": {{
      "command": "uvx",
      "args": ["cailculator-mcp"],
      "env": {{
        "CAILCULATOR_API_KEY": "{api_key}"
      }}
    }}
  }}
}}

4. Restart Claude Desktop

Documentation: https://github.com/pchavez2029/CAILculator
Support: iknowpi@gmail.com

Features included in your {tier_display} plan:
- All 5 MCP tools (compute, transform, patterns, analysis, visualizations)
- Dual framework support (Cayley-Dickson + Clifford)
- 16D-256D dimensional range
- Chavez Transform data analysis
- Canonical Six pattern detection

Better math, less suffering.

— Chavez AI Labs

---
Need help? Reply to this email or reach out at iknowpi@gmail.com
    """.strip()

    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"✅ Sent API key to {email}")

    except Exception as e:
        print(f"❌ Failed to send email to {email}: {e}")
        print(f"   API key (manual delivery needed): {api_key}")


# Note: store_api_key is now imported from database.py


@app.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """
    Handle Stripe webhook events

    Key events:
    - checkout.session.completed: Customer completed checkout
    - customer.subscription.created: Subscription was created
    - customer.subscription.updated: Subscription changed (upgrade/downgrade)
    - customer.subscription.deleted: Subscription cancelled
    """
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({"error": "Invalid signature"}), 400

    print(f"📥 Received event: {event['type']}")

    # Handle checkout completion
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Extract details
        customer_id = session.get('customer')
        customer_email = session.get('customer_details', {}).get('email')
        customer_name = session.get('customer_details', {}).get('name')
        subscription_id = session.get('subscription')

        if not subscription_id:
            print("⚠️  No subscription in checkout session")
            return jsonify({"received": True}), 200

        # Get subscription to determine tier
        subscription = stripe.Subscription.retrieve(subscription_id)
        price_id = subscription['items']['data'][0]['price']['id']

        # Map price ID to tier (LIVE MODE - updated 2025-10-29)
        tier_map = {
            "price_1SNlPU2NNm10BnLC1ufwG07s": "individual",   # $79.99/month
            "price_1SNlQz2NNm10BnLC3wFUtekN": "academic",     # $199/month
            "price_1SNlUg2NNm10BnLCy2NhebOI": "commercial",   # $299/month
        }

        tier = tier_map.get(price_id, "individual")  # Default to individual

        # Generate API key
        api_key = generate_api_key(tier)

        # Store in database
        store_api_key(api_key, customer_id, subscription_id, tier, customer_email)

        # Send email with API key
        send_api_key_email(customer_email, api_key, tier, customer_name)

        print(f"✅ Generated key for {customer_email}: {api_key}")

    # Handle subscription created (backup event)
    elif event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        customer_id = subscription['customer']

        # Get customer details
        customer = stripe.Customer.retrieve(customer_id)
        email = customer.get('email')
        name = customer.get('name')

        # Similar logic to checkout.session.completed
        # ... (implement if needed)

    # Handle subscription cancellation
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        subscription_id = subscription['id']

        # Deactivate API keys in database
        print(f"🔒 Deactivating keys for subscription: {subscription_id}")
        deactivate_subscription(subscription_id)

    return jsonify({"received": True}), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "cailculator-webhook-handler",
        "timestamp": datetime.utcnow().isoformat()
    }), 200


@app.route('/init-db', methods=['GET'])
def init_db_endpoint():
    """
    ONE-TIME database initialization endpoint
    Visit this URL once to create the api_keys table

    IMPORTANT: Remove this endpoint after first use for security!
    """
    from database import init_database

    try:
        init_database()
        return jsonify({
            "success": True,
            "message": "✅ Database initialized successfully!",
            "note": "You can now remove this /init-db endpoint from the code"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    print(f"🚀 Webhook handler starting on port {port}")
    print(f"📧 Email configured: {bool(SMTP_USER and SMTP_PASSWORD)}")
    app.run(host='0.0.0.0', port=port)
