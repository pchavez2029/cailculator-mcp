"""
Stripe Product Catalog Setup for CAILculator (Premium)

Products:
- Individual: $79.99/month
- Academic: $199/month
- Commercial: $299/month (quantity-based)

Coupons:
- ANTHROPIC50: 50% off for Anthropic
- GOOGLE50: 50% off for Google
- STUDENT80: 80% off for students
- YC2025: 100% off for YC batch
"""

import stripe
import os
import sys

from dotenv import load_dotenv
load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

if not stripe.api_key:
    print("❌ Set STRIPE_SECRET_KEY environment variable")
    sys.exit(1)

print("="*80)
print("CAILCULATOR PREMIUM SETUP")
print("="*80)
print()

# ============================================================================
# PRODUCTS
# ============================================================================

print("Creating products...")
print("-"*80)

# Individual: $79.99/month
individual = stripe.Product.create(
    name="CAILculator Individual",
    description="High-dimensional algebra analysis for independent researchers",
    metadata={"tier": "individual"}
)
individual_price = stripe.Price.create(
    product=individual.id,
    unit_amount=7999,
    currency="usd",
    recurring={"interval": "month"}
)
print(f"✅ Individual: ${individual_price.unit_amount/100:.2f}/month")
print(f"   Product: {individual.id}")
print(f"   Price: {individual_price.id}")
print()

# Academic: $199/month
academic = stripe.Product.create(
    name="CAILculator Academic",
    description="Research-grade tooling for academic institutions",
    metadata={"tier": "academic"}
)
academic_price = stripe.Price.create(
    product=academic.id,
    unit_amount=19900,
    currency="usd",
    recurring={"interval": "month"}
)
print(f"✅ Academic: ${academic_price.unit_amount/100:.2f}/month")
print(f"   Product: {academic.id}")
print(f"   Price: {academic_price.id}")
print()

# Commercial: $299/month (volume pricing)
commercial = stripe.Product.create(
    name="CAILculator Commercial",
    description="Production-grade high-dimensional analysis",
    metadata={"tier": "commercial"}
)
commercial_price = stripe.Price.create(
    product=commercial.id,
    unit_amount=29900,
    currency="usd",
    recurring={"interval": "month"}
)
print(f"✅ Commercial: ${commercial_price.unit_amount/100:.2f}/month per seat")
print(f"   Product: {commercial.id}")
print(f"   Price: {commercial_price.id}")
print()

# ============================================================================
# COUPONS
# ============================================================================

print("Creating coupons...")
print("-"*80)

def create_coupon(id, percent, months, desc, max_uses=None):
    try:
        params = {
            "id": id,
            "percent_off": percent,
            "duration": "repeating",
            "duration_in_months": months,
            "metadata": {"description": desc}
        }
        if max_uses:
            params["max_redemptions"] = max_uses

        coupon = stripe.Coupon.create(**params)
        print(f"✅ {coupon.id}: {coupon.percent_off}% off for {months} months")
        if max_uses:
            print(f"   Max uses: {max_uses}")
        return coupon
    except stripe.error.StripeError as e:
        if "already exists" in str(e).lower():
            print(f"ℹ️  {id} already exists")
        else:
            print(f"❌ Error: {e}")
        return None

# Anthropic: 50% off for 12 months
create_coupon("ANTHROPIC50", 50, 12, "Anthropic employees", max_uses=500)

# Google: 50% off for 12 months
create_coupon("GOOGLE50", 50, 12, "Google employees", max_uses=500)

# Students: 80% off for 12 months
create_coupon("STUDENT80", 80, 12, "Students (requires .edu)", max_uses=1000)

# YC 2025: 100% off for 12 months
create_coupon("YC2025", 100, 12, "YC W25/S25 batch", max_uses=300)

print()

# ============================================================================
# SUMMARY
# ============================================================================

print("="*80)
print("✅ SETUP COMPLETE")
print("="*80)
print()
print("Products:")
print("  - Individual: $79.99/month")
print("  - Academic: $199/month")
print("  - Commercial: $299/month")
print()
print("Coupons:")
print("  - ANTHROPIC50: 50% off")
print("  - GOOGLE50: 50% off")
print("  - STUDENT80: 80% off")
print("  - YC2025: 100% off (your batch!)")
print()
print("Next steps:")
print("  1. Create payment links at: dashboard.stripe.com/payment-links")
print("  2. Set up webhook at: dashboard.stripe.com/webhooks")
print("     Endpoint: https://cailculator-auth.railway.app/webhooks/stripe")
print("     Events: checkout.session.completed, customer.subscription.created")
print("  3. Test with card: 4242 4242 4242 4242")
print()
