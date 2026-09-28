# 🚚 FreightLedger AI

An AI-powered invoice extraction and validation agent for the freight and logistics industry.

## 🎯 What It Does

- Reads freight invoice PDFs (text-based AND scanned images)
- Extracts: Invoice Number, Date, Vendor, Total Amount, Currency, Line Items
- Validates data against business rules
- Stores results in a SQLite database
- Exposes a REST API (FastAPI)
- Provides a web UI (Streamlit)

## 🛠️ Tech Stack

- **LLM:** Groq (Llama 3.3 70B) — 100% Free
- **Framework:** LangChain
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **PDF Parsing:** pdfplumber, pytesseract, pdf2image
- **Database:** SQLite + SQLAlchemy

## 🚀 Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/freightledger-ai.git
cd freightledger-ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Edit .env with your Groq API key
uvicorn main:app --reload
# In a second terminal:
streamlit run app.py