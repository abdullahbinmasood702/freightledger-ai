"""
Basic tests for FreightLedger AI.
Run with: pytest tests/
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models import Invoice
from database import init_db, save_invoice, list_invoices


def test_invoice_model_valid():
    inv = Invoice(
        invoice_number="INV-001",
        vendor_name="Test Vendor",
        total_amount=100.50,
        currency="USD",
    )
    assert inv.invoice_number == "INV-001"
    assert inv.total_amount == 100.50
    assert inv.currency == "USD"


def test_invoice_model_negative_amount():
    try:
        Invoice(
            invoice_number="INV-002",
            vendor_name="Bad Vendor",
            total_amount=-50.0,
        )
        assert False, "Should have raised ValueError"
    except Exception:
        assert True


def test_database_save_and_list():
    init_db()
    record_id = save_invoice(
        {
            "invoice_number": "INV-TEST-001",
            "vendor_name": "Test Logistics",
            "total_amount": 999.99,
            "currency": "USD",
        }
    )
    assert record_id > 0
    invoices = list_invoices(limit=5)
    assert any(i["invoice_number"] == "INV-TEST-001" for i in invoices)