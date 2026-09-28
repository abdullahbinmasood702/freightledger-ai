"""
FreightLedger AI — Core extraction agent using LangChain + Groq.
"""
import os
import json
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from tools.pdf_tool import extract_text_from_pdf
from tools.ocr_tool import extract_text_with_ocr

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY or GROQ_API_KEY.startswith("gsk_your"):
    raise ValueError(
        "Please set GROQ_API_KEY in your .env file. "
        "Get one free at https://console.groq.com"
    )

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=GROQ_API_KEY,
    max_tokens=2000,
)

tools = [extract_text_from_pdf, extract_text_with_ocr]

# Hardcoded ReAct prompt (no hub.pull dependency)
REACT_PROMPT = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

prompt = PromptTemplate.from_template(REACT_PROMPT)

agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=25,
    max_execution_time=180,
    early_stopping_method="force",
    return_intermediate_steps=False,
)


def _clean_json(raw: str) -> str:
    """Extract the JSON object from the LLM output."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?", "", raw, flags=re.MULTILINE).strip()
    raw = re.sub(r"```$", "", raw, flags=re.MULTILINE).strip()

    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1:
        return raw[start : end + 1]
    return raw


def extract_invoice_data(pdf_path: str) -> dict:
    """
    Run the agent on a PDF invoice and return a structured dict.
    """
    if not os.path.exists(pdf_path):
        return {"status": "error", "error": f"File not found: {pdf_path}"}

    query = f"""
Extract data from the freight invoice at this exact path: '{pdf_path}'

Steps:
1. Use the extract_text_from_pdf tool with input = '{pdf_path}'
2. If that returns an error about scanned images, use extract_text_with_ocr with input = '{pdf_path}'
3. From the extracted text, identify these fields:
   - invoice_number
   - invoice_date (YYYY-MM-DD)
   - vendor_name
   - total_amount (number only, no currency symbols)
   - currency (USD, PKR, EUR, etc.)
   - line_items (list of objects with description, quantity, unit_price, total)

Return ONLY a valid JSON object. No markdown. No explanation.

Example:
{{
  "invoice_number": "INV-12345",
  "invoice_date": "2026-01-15",
  "vendor_name": "Acme Freight Co.",
  "total_amount": 1250.50,
  "currency": "USD",
  "line_items": [
    {{"description": "Shipping", "quantity": 1, "unit_price": 1250.50, "total": 1250.50}}
  ]
}}
"""

    try:
        response = agent_executor.invoke({"input": query})
        raw_output = response.get("output", "")

        cleaned = _clean_json(raw_output)

        try:
            data = json.loads(cleaned)

            # If the LLM returned an error object, mark it as error
            if "error" in data and "invoice_number" not in data:
                return {
                    "status": "error",
                    "error": data.get("error", "Unknown extraction error"),
                    "raw_output": raw_output,
                }

            data["status"] = "success"
            return data

        except json.JSONDecodeError as je:
            return {
                "status": "partial",
                "error": f"JSON parse failed: {je}",
                "raw_output": raw_output,
            }

    except Exception as e:
        return {"status": "error", "error": f"Agent error: {str(e)}"}


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python agent.py <path_to_pdf>")
        sys.exit(1)

    result = extract_invoice_data(sys.argv[1])
    print("\n--- EXTRACTED DATA ---")
    print(json.dumps(result, indent=2))