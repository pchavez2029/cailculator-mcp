"""
Database migration script to update schema
Adds missing columns to existing tables
"""

import os
from sqlalchemy import create_engine, text

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    exit(1)

engine = create_engine(DATABASE_URL)

def migrate():
    """Add missing columns to users table"""
    with engine.connect() as conn:
        try:
            # Add email_verified column if not exists
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS email_verified INTEGER DEFAULT 0 NOT NULL
            """))
            print("✓ Added email_verified column")

            # Add verification_token column if not exists
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS verification_token VARCHAR
            """))
            print("✓ Added verification_token column")

            # Add verification_token_expires column if not exists
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS verification_token_expires TIMESTAMP
            """))
            print("✓ Added verification_token_expires column")

            # Add country_code column if not exists
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS country_code VARCHAR(2)
            """))
            print("✓ Added country_code column")

            # Add signup_ip column if not exists
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS signup_ip VARCHAR
            """))
            print("✓ Added signup_ip column")

            # Add requires_manual_approval column if not exists
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS requires_manual_approval INTEGER DEFAULT 0 NOT NULL
            """))
            print("✓ Added requires_manual_approval column")

            # Create index on verification_token if not exists
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_users_verification_token
                ON users(verification_token)
            """))
            print("✓ Created verification_token index")

            conn.commit()
            print("\n✅ Migration completed successfully!")

        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            conn.rollback()
            raise

if __name__ == "__main__":
    print("Starting database migration...\n")
    migrate()
