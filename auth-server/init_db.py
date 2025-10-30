"""
Initialize CAILculator database schema
Run this ONCE after deploying to Railway

Usage:
  python init_db.py
"""

from database import init_database

if __name__ == "__main__":
    print("="*60)
    print("CAILCULATOR DATABASE INITIALIZATION")
    print("="*60)
    print()
    print("This will create the api_keys table and indexes.")
    print()

    try:
        init_database()
        print()
        print("="*60)
        print("✅ SUCCESS! Database is ready.")
        print("="*60)
    except Exception as e:
        print()
        print("="*60)
        print(f"❌ ERROR: {e}")
        print("="*60)
        print()
        print("Troubleshooting:")
        print("  - Check DATABASE_URL is set in Railway")
        print("  - Ensure PostgreSQL database is running")
        print("  - Check database credentials")
