"""
Database module for CAILculator API key management
Uses PostgreSQL (provisioned by Railway)
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from contextlib import contextmanager

DATABASE_URL = os.getenv("DATABASE_URL")

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database():
    """
    Initialize database schema
    Run this once to create the api_keys table
    """
    with get_db() as conn:
        cur = conn.cursor()

        # Create api_keys table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id SERIAL PRIMARY KEY,
                api_key VARCHAR(100) UNIQUE NOT NULL,
                customer_id VARCHAR(100) NOT NULL,
                subscription_id VARCHAR(100) NOT NULL,
                tier VARCHAR(50) NOT NULL,
                email VARCHAR(255) NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for fast lookups
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_api_key ON api_keys(api_key)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_subscription ON api_keys(subscription_id)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_customer ON api_keys(customer_id)
        """)

        print("✅ Database schema initialized")


def store_api_key(api_key: str, customer_id: str, subscription_id: str,
                  tier: str, email: str) -> bool:
    """
    Store a new API key in the database

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO api_keys
                (api_key, customer_id, subscription_id, tier, email, status)
                VALUES (%s, %s, %s, %s, %s, 'active')
            """, (api_key, customer_id, subscription_id, tier, email))

            print(f"✅ Stored API key in database: {api_key[:20]}... -> {email}")
            return True

    except Exception as e:
        print(f"❌ Error storing API key: {e}")
        return False


def validate_api_key(api_key: str) -> dict:
    """
    Validate an API key and return subscription info

    Returns:
        dict with keys: valid (bool), tier, usage_count, limit, error (if invalid)
    """
    try:
        with get_db() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT api_key, tier, email, status, usage_count, created_at
                FROM api_keys
                WHERE api_key = %s
            """, (api_key,))

            result = cur.fetchone()

            if not result:
                return {
                    "valid": False,
                    "error": "API key not found"
                }

            if result['status'] != 'active':
                return {
                    "valid": False,
                    "error": f"API key is {result['status']}"
                }

            # Define usage limits by tier
            limits = {
                "individual": 10000,
                "academic": 50000,
                "commercial": 100000
            }

            limit = limits.get(result['tier'], 10000)

            # Check if over limit
            if result['usage_count'] >= limit:
                return {
                    "valid": False,
                    "error": "Usage limit exceeded",
                    "usage": result['usage_count'],
                    "limit": limit
                }

            # Increment usage count
            cur.execute("""
                UPDATE api_keys
                SET usage_count = usage_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE api_key = %s
            """, (api_key,))

            return {
                "valid": True,
                "tier": result['tier'],
                "email": result['email'],
                "usage": result['usage_count'] + 1,
                "limit": limit
            }

    except Exception as e:
        print(f"❌ Error validating API key: {e}")
        return {
            "valid": False,
            "error": "Database error"
        }


def deactivate_subscription(subscription_id: str) -> bool:
    """
    Deactivate all API keys associated with a subscription
    Called when subscription is cancelled

    Returns:
        bool: True if successful
    """
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE api_keys
                SET status = 'cancelled',
                    updated_at = CURRENT_TIMESTAMP
                WHERE subscription_id = %s
            """, (subscription_id,))

            rows_affected = cur.rowcount
            print(f"✅ Deactivated {rows_affected} API key(s) for subscription {subscription_id}")
            return True

    except Exception as e:
        print(f"❌ Error deactivating subscription: {e}")
        return False


def get_subscription_info(subscription_id: str) -> dict:
    """
    Get all API keys for a subscription
    Useful for customer support
    """
    try:
        with get_db() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT api_key, tier, email, status, usage_count, created_at
                FROM api_keys
                WHERE subscription_id = %s
            """, (subscription_id,))

            results = cur.fetchall()
            return {
                "found": len(results),
                "keys": [dict(row) for row in results]
            }

    except Exception as e:
        print(f"❌ Error getting subscription info: {e}")
        return {"found": 0, "keys": [], "error": str(e)}


if __name__ == "__main__":
    """Run this to initialize the database"""
    print("Initializing CAILculator database...")
    init_database()
    print("Done!")
