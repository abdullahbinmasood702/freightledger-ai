"""
Generate a real, text-based sample freight invoice PDF for testing.
"""
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=12)

# Title
pdf.set_font("Helvetica", "B", size=18)
pdf.cell(0, 12, "FREIGHT INVOICE", ln=True, align="C")
pdf.ln(8)

# Header info
pdf.set_font("Helvetica", size=12)
pdf.cell(0, 8, "Invoice Number: INV-2026-0042", ln=True)
pdf.cell(0, 8, "Invoice Date: 2026-01-15", ln=True)
pdf.cell(0, 8, "Vendor: Lahore Cargo Services", ln=True)
pdf.cell(0, 8, "Currency: PKR", ln=True)
pdf.ln(6)

# Line items header
pdf.set_font("Helvetica", "B", size=12)
pdf.cell(90, 8, "Description", border=1)
pdf.cell(25, 8, "Qty", border=1, align="C")
pdf.cell(35, 8, "Unit Price", border=1, align="R")
pdf.cell(40, 8, "Total", border=1, align="R", ln=True)

# Line items
pdf.set_font("Helvetica", size=11)
items = [
    ("Container shipping Lahore to Karachi", "1", "45000", "45000"),
    ("Customs clearance", "1", "8500", "8500"),
]
for desc, qty, unit, total in items:
    pdf.cell(90, 8, desc, border=1)
    pdf.cell(25, 8, qty, border=1, align="C")
    pdf.cell(35, 8, unit, border=1, align="R")
    pdf.cell(40, 8, total, border=1, align="R", ln=True)

# Total
pdf.ln(4)
pdf.set_font("Helvetica", "B", size=13)
pdf.cell(150, 10, "TOTAL AMOUNT:", align="R")
pdf.cell(40, 10, "53500", align="R", ln=True)

pdf.output("invoices/sample_invoice.pdf")
print("✅ Real PDF created: invoices/sample_invoice.pdf")