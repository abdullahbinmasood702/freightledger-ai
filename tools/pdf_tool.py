"""
FreightLedger AI — PDF text extraction tool.
Extracts text from text-based PDFs using pdfplumber.
"""
import os
import pdfplumber
from langchain.tools import tool


@tool
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a text-based PDF invoice file.
    Provide the full file path as input.
    If the PDF has no extractable text (scanned image), return an error hinting to use OCR.
    """
    if not pdf_path or not pdf_path.lower().endswith(".pdf"):
        return "Error: Please provide a valid PDF file path."

    if not os.path.exists(pdf_path):
        return f"Error: File not found at {pdf_path}"

    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num} ---\n"
                    text += page_text + "\n"

        if not text.strip():
            return (
                "Error: No extractable text found in PDF. "
                "This is likely a scanned image. Please use extract_text_with_ocr."
            )

        max_chars = 12000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[... truncated for length ...]"

        return text

    except Exception as e:
        return f"Error extracting text: {str(e)}"