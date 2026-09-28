"""
FreightLedger AI — Streamlit UI (Direct Agent Version for Cloud Deploy)
"""
import streamlit as st
import os
import json
from dotenv import load_dotenv

# Load environment variables (for local testing)
load_dotenv()

# Import the agent directly
from agent import extract_invoice_data
from database import init_db, save_invoice, list_invoices

# Initialize database
init_db()

st.set_page_config(
    page_title="FreightLedger AI",
    page_icon="🚚",
    layout="wide",
)

st.title("🚚 FreightLedger AI")
st.markdown("### AI-powered freight invoice extraction — built with $0 investment")

tab1, tab2 = st.tabs(["📤 Extract Invoice", "📋 History"])

with tab1:
    st.markdown("Upload a freight invoice PDF. The AI will extract all key fields automatically.")
    uploaded_file = st.file_uploader("Choose a PDF invoice", type=["pdf"])

    if uploaded_file is not None:
        col1, col2 = st.columns([1, 2])

        with col1:
            st.info(
                f"**File:** {uploaded_file.name}\n\n"
                f"**Size:** {len(uploaded_file.getvalue()) / 1024:.1f} KB"
            )

        with col2:
            if st.button("🚀 Extract Data", type="primary", use_container_width=True):
                with st.spinner("AI is reading your invoice..."):
                    try:
                        # Save uploaded file temporarily
                        temp_path = os.path.join("invoices", uploaded_file.name)
                        os.makedirs("invoices", exist_ok=True)
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getvalue())

                        # Run agent directly
                        result = extract_invoice_data(temp_path)

                        if result.get("status") == "success":
                            # Save to database
                            record_id = save_invoice(result)
                            st.success(f"✅ Extraction successful! Record ID: {record_id}")
                            st.json(result)
                        elif result.get("status") == "partial":
                            st.warning("⚠️ Partial extraction. Raw output below:")
                            st.code(result.get("raw_output", result.get("error", "")), language="json")
                        else:
                            st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                            if result.get("raw_output"):
                                st.code(result["raw_output"])
                    except Exception as e:
                        st.error(f"Unexpected error: {e}")

with tab2:
    st.markdown("### Previously processed invoices")

    if st.button("🔄 Refresh"):
        st.rerun()

    try:
        invoices = list_invoices(limit=20)
        if invoices:
            st.dataframe(invoices, use_container_width=True)
        else:
            st.info("No invoices processed yet.")
    except Exception as e:
        st.error(f"Failed to load invoices: {e}")

st.markdown("---")
st.caption("Built with free Groq API • LangChain • Streamlit")