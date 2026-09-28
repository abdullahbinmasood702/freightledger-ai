"""
FreightLedger AI — FastAPI backend.
"""
import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from agent import extract_invoice_data
from models import Invoice
from database import init_db, save_invoice, list_invoices

load_dotenv()

app = FastAPI(
    title="FreightLedger AI",
    description="AI-powered freight invoice extraction & validation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "invoices")
os.makedirs(UPLOAD_DIR, exist_ok=True)
init_db()


@app.get("/health")
def health():
    return {"status": "ok", "service": "FreightLedger AI"}


@app.post("/extract")
async def extract_invoice(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = extract_invoice_data(file_path)

    if result.get("status") == "success":
        try:
            clean_data = {k: v for k, v in result.items() if k != "status"}
            invoice = Invoice(**clean_data)
            record_id = save_invoice(invoice.model_dump())
            return JSONResponse(
                content={
                    "status": "success",
                    "record_id": record_id,
                    "invoice": invoice.model_dump(),
                }
            )
        except Exception as e:
            return JSONResponse(
                content={
                    "status": "partial",
                    "error": f"Validation failed: {str(e)}",
                    "raw_output": result,
                }
            )

    return JSONResponse(content=result)


@app.get("/invoices")
def get_invoices(limit: int = 50):
    return {"invoices": list_invoices(limit=limit)}