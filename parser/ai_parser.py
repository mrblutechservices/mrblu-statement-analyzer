import os
import json
import pdfplumber
from dotenv import load_dotenv
from openai import OpenAI

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF"""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def ask_ai_to_extract_transactions(text):
    """Send PDF text to AI and get transactions JSON"""

    prompt = f"""
You are reading a bank statement table.

The table columns are in this exact order:

Date | Value Date | Narration | Chq No | Withdrawal | Deposit | Balance

Rules:
- Withdrawal column = Debit
- Deposit column = Credit
- Do NOT guess.
- Read numbers from correct column position.
- If Withdrawal has value → debit
- If Deposit has value → credit
- Balance is running balance

Return ONLY JSON array:

[
  {{
    "date": "",
    "description": "",
    "debit": 0,
    "credit": 0,
    "balance": 0,
    "party": ""
  }}
]

Bank Statement Text:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    ai_output = response.choices[0].message.content
    return ai_output


def parse_ai_json(ai_text):
    """Convert AI text response to Python JSON"""
    try:
        # Find JSON inside response
        start = ai_text.find("[")
        end = ai_text.rfind("]") + 1
        json_text = ai_text[start:end]

        data = json.loads(json_text)
        return data
    except Exception as e:
        print("AI JSON parse error:", e)
        return []


def ai_parse_transactions(pdf_path):
    """Main AI parser function"""
    print("AI parsing started...")

    text = extract_text_from_pdf(pdf_path)

    if not text:
        print("No text found in PDF")
        return []

    ai_response = ask_ai_to_extract_transactions(text)
    transactions = parse_ai_json(ai_response)

    print(f"AI extracted {len(transactions)} transactions")
    return transactions