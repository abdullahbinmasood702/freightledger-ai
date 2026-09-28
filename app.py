"""
FreightLedger AI — Streamlit UI.
"""
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="FreightLedger AI",
    page_icon="🚚",
    layout="wide",
)

st.title("🚚 FreightLedger AI")
st.markdown("### AI-powered freight invoice extraction — built with $0 investment")

tab1, tab2 = st.tabs(["📤 Extract Invoice", "📋 History"])

with tab1:
    st.markdown(
        "Upload a freight invoice PDF. The AI will extract all key fields automatically."
    )
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
                        files = {
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                "application/pdf",
                            )
                        }
                        response = requests.post(
                            f"{API_URL}/extract", files=files, timeout=180
                        )

                        if response.status_code == 200:
                            data = response.json()

                            if data.get("status") == "success":
                                st.success(
                                    f"✅ Extraction successful! "
                                    f"Record ID: {data.get('record_id', 'N/A')}"
                                )
                                st.json(data["invoice"])
                            elif data.get("status") == "partial":
                                st.warning("⚠️ Partial extraction. Raw output below:")
                                st.code(
                                    data.get("raw_output", data.get("error", "")),
                                    language="json",
                                )
                            else:
                                st.error(
                                    f"❌ Error: {data.get('error', 'Unknown error')}"
                                )
                                if data.get("raw_output"):
                                    st.code(data["raw_output"])
                        else:
                            st.error(f"HTTP {response.status_code}: {response.text}")

                    except requests.exceptions.ConnectionError:
                        st.error(
                            "❌ Cannot connect to the backend.\n\n"
                            "Make sure the FastAPI server is running:\n"
                            "```\nuvicorn main:app --reload\n```"
                        )
                    except Exception as e:
                        st.error(f"Unexpected error: {e}")

with tab2:
    st.markdown("### Previously processed invoices")

    if st.button("🔄 Refresh"):
        st.rerun()

    try:
        response = requests.get(f"{API_URL}/invoices?limit=20", timeout=10)
        if response.status_code == 200:
            invoices = response.json().get("invoices", [])
            if invoices:
                st.dataframe(invoices, use_container_width=True)
            else:
                st.info("No invoices processed yet.")
        else:
            st.error(f"Failed to load invoices: HTTP {response.status_code}")
    except Exception:
        st.info("Start the backend to see invoice history.")

st.markdown("---")
st.caption("Built with free Groq API • LangChain • FastAPI • Streamlit")