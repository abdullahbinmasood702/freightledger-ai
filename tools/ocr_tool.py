"""
FreightLedger AI — OCR tool for scanned PDFs.
Uses pdf2image + pytesseract to extract text from image-based PDFs.
"""
import os
from langchain.tools import tool

try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


@tool
def extract_text_with_ocr(pdf_path: str) -> str:
    """
    Extract text from a scanned/image-based PDF using OCR.
    Use this when extract_text_from_pdf fails.
    Provide the full file path as input.
    """
    if not OCR_AVAILABLE:
        return (
            "Error: OCR libraries not installed. "
            "Install with: pip install pdf2image pytesseract Pillow. "
            "Also install Tesseract-OCR and Poppler on your system."
        )

    if not pdf_path or not pdf_path.lower().endswith(".pdf"):
        return "Error: Please provide a valid PDF file path."

    if not os.path.exists(pdf_path):
        return f"Error: File not found at {pdf_path}"

    try:
        images = convert_from_path(pdf_path, dpi=300)
        text = ""
        for i, image in enumerate(images, 1):
            page_text = pytesseract.image_to_string(image)
            if page_text.strip():
                text += f"\n--- Page {i} (OCR) ---\n"
                text += page_text + "\n"

        if not text.strip():
            return "Error: OCR returned no text. The image may be too low quality."

        max_chars = 12000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[... truncated for length ...]"

        return text

    except Exception as e:
        return f"OCR error: {str(e)}"