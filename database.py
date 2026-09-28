"""
FreightLedger AI — SQLite database with SQLAlchemy.
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./freightledger.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class InvoiceRecord(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, index=True)
    invoice_date = Column(String, nullable=True)
    vendor_name = Column(String, index=True)
    total_amount = Column(Float)
    currency = Column(String, default="USD")
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_invoice(invoice_data: dict) -> int:
    """Save an invoice dict to the database. Returns the new record ID."""
    db = SessionLocal()
    try:
        record = InvoiceRecord(
            invoice_number=invoice_data.get("invoice_number", "UNKNOWN"),
            invoice_date=str(invoice_data.get("invoice_date", "")),
            vendor_name=invoice_data.get("vendor_name", "UNKNOWN"),
            total_amount=float(invoice_data.get("total_amount", 0.0)),
            currency=invoice_data.get("currency", "USD"),
            raw_text=(invoice_data.get("raw_text") or "")[:5000],
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.id
    finally:
        db.close()


def list_invoices(limit: int = 50) -> list:
    """Return the most recent invoices."""
    db = SessionLocal()
    try:
        records = (
            db.query(InvoiceRecord)
            .order_by(InvoiceRecord.id.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "invoice_number": r.invoice_number,
                "vendor_name": r.vendor_name,
                "total_amount": r.total_amount,
                "currency": r.currency,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ]
    finally:
        db.close()