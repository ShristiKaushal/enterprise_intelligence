"""
Database initialization and seeding script.
Run once to create tables and add a demo admin user.
Usage: python scripts/init_db.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.security import hash_password
from app.database.session import AsyncSessionLocal, create_all_tables
from app.models.user import User
from sqlalchemy import select

configure_logging()
logger = get_logger("init_db")


DEMO_USERS = [
    {"email": "admin@eip.local", "username": "admin", "full_name": "Platform Admin", "password": "Admin@12345", "role": "admin"},
    {"email": "analyst@eip.local", "username": "analyst", "full_name": "Data Analyst", "password": "Analyst@12345", "role": "analyst"},
    {"email": "viewer@eip.local", "username": "viewer", "full_name": "Dashboard Viewer", "password": "Viewer@12345", "role": "viewer"},
]


async def main() -> None:
    logger.info("Initializing database…", db_url=settings.DATABASE_URL.split("@")[-1])

    # Create all tables
    await create_all_tables()
    logger.info("Tables created")

    # Seed users
    async with AsyncSessionLocal() as session:
        for u_data in DEMO_USERS:
            result = await session.execute(select(User).where(User.email == u_data["email"]))
            existing = result.scalar_one_or_none()
            if existing:
                logger.info("User already exists", email=u_data["email"])
                continue
            user = User(
                email=u_data["email"],
                username=u_data["username"],
                full_name=u_data["full_name"],
                hashed_password=hash_password(u_data["password"]),
                role=u_data["role"],
                is_active=True,
                is_verified=True,
            )
            session.add(user)
            logger.info("Created user", email=u_data["email"], role=u_data["role"])
        await session.commit()

    logger.info("Database initialization complete!")
    print("\n[OK] Database ready!")
    print("   Demo users:")
    for u in DEMO_USERS:
        print(f"   - {u['role'].upper()}: {u['email']} / {u['password']}")
    print("\n   Start the backend:  uvicorn app.main:app --reload")
    print("   Start the frontend: cd ../frontend && npm run dev\n")


if __name__ == "__main__":
    asyncio.run(main())
