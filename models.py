"""
FreightLedger AI — Pydantic models for invoice validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class LineItem(BaseModel):
    """A single line item on an invoice."""
    description: str = Field(..., description="Description of the item")
    quantity: Optional[float] = Field(None, description="Quantity")
    unit_price: Optional[float] = Field(None, description="Price per unit")
    total: Optional[float] = Field(None, description="Line total")


class Invoice(BaseModel):
    """A complete freight invoice."""
    invoice_number: str = Field(..., description="Unique invoice identifier")
    invoice_date: Optional[str] = Field(None, description="Invoice date (YYYY-MM-DD)")
    vendor_name: str = Field(..., description="Name of the vendor")
    total_amount: float = Field(..., description="Total amount due")
    currency: str = Field(default="USD", description="Currency code")
    line_items: List[LineItem] = Field(default_factory=list)
    raw_text: Optional[str] = Field(None, description="Raw extracted text for auditing")
    processed_at: Optional[str] = Field(default=None, description="Processing timestamp")

    @field_validator("total_amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("Total amount cannot be negative")
        return v

    @field_validator("currency")
    @classmethod
    def currency_must_be_valid(cls, v):
        valid = ["USD", "PKR", "EUR", "GBP", "AED", "SAR", "INR", "CNY"]
        v_upper = v.upper()
        if v_upper not in valid:
            return "USD"
        return v_upper


class InvoiceResponse(BaseModel):
    """Response wrapper for API."""
    status: str
    invoice: Optional[Invoice] = None
    raw_output: Optional[str] = None
    error: Optional[str] = None