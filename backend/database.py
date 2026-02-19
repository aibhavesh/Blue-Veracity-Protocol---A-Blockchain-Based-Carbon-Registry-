"""
SQLAlchemy database models and configuration
"""

import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///./blue_veracity.db"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base
Base = declarative_base()


class CarbonCreditDB(Base):
    """
    Database model for carbon credit submissions
    """

    __tablename__ = "carbon_credits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    wallet_address = Column(String, index=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    ipfs_hash = Column(String, unique=True, index=True, nullable=False)
    credits_amount = Column(Float, nullable=False)
    file_name = Column(String, nullable=False)
    status = Column(String, default="PENDING", index=True)  # PENDING, VERIFIED, FAILED
    transaction_hash = Column(String, unique=True, nullable=True, index=True)
    token_id = Column(Integer, nullable=True, unique=True, index=True)
    metadata_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    verified_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<CarbonCredit id={self.id} status={self.status} credits={self.credits_amount}>"


def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        raise


def get_db_session():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
