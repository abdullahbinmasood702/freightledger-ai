"""
FreightLedger AI — Email summary tool.
Logs email content to a file (SMTP integration coming soon).
"""
import os
from langchain.tools import tool


@tool
def send_summary_email(recipient: str, subject: str, body: str) -> str:
    """
    Send a summary email to a recipient.
    Currently logs to a file — SMTP integration can be added later.
    Provide: recipient, subject, body as inputs.
    """
    try:
        log_path = "data/email_log.txt"
        os.makedirs("data", exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"TO: {recipient}\n")
            f.write(f"SUBJECT: {subject}\n")
            f.write(f"BODY:\n{body}\n")
            f.write("-" * 50 + "\n")
        return f"Email logged successfully to {log_path}."
    except Exception as e:
        return f"Error logging email: {str(e)}"