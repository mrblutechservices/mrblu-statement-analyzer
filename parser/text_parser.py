import pdfplumber
import re

date_pattern = r"\b(\d{2}[-/]\d{2}[-/]\d{4}|\d{2}-[A-Za-z]{3}-\d{2,4}|\d{2} [A-Za-z]{3} \d{4})\b"


def clean_amount(x):

    if not x:
        return ""

    x = str(x)

    x = x.replace(",", "")
    x = x.replace("CR", "")
    x = x.replace("Cr", "")
    x = x.replace("DR", "")
    x = x.replace("Dr", "")

    return x.strip()


def parse_text(file):

    transactions = []

    with pdfplumber.open(file) as pdf:

        text = ""

        for page in pdf.pages:

            t = page.extract_text()

            if t:
                text += t + "\n"

    lines = text.split("\n")

    for line in lines:

        line = line.strip()

        skip_words = [
            "STATEMENT",
            "ACCOUNT STATEMENT",
            "OPENING BALANCE",
            "CLOSING BALANCE",
            "TOTAL CREDIT",
            "TOTAL DEBIT",
            "DESCRIPTION",
            "PARTICULARS",
        ]

        if any(x in line.upper() for x in skip_words):
            continue

        if not re.search(date_pattern, line):
            continue

        nums = re.findall(r"\d[\d,]*\.\d{2}\s*(?:CR|DR|Cr|Dr)?", line)

        debit = ""
        credit = ""
        balance = ""

        if nums:

            amount_raw = nums[-1]
            amount = clean_amount(amount_raw)

            if "CR" in amount_raw.upper():
                credit = amount
            elif "DR" in amount_raw.upper():
                debit = amount
            else:
                debit = amount

            if len(nums) >= 2:
                balance = clean_amount(nums[-1])

        # Extract date
        date_match = re.search(date_pattern, line)

        date_val = ""

        if date_match:
            date_val = date_match.group(0)

        transactions.append({

            "Date": date_val,
            "Value_Date": "",
            "Description": line.strip(),
            "Cheque_No": "",
            "Debit": debit,
            "Credit": credit,
            "Balance": balance,
            "Branch_Code": "",
            "Party": "",
            "Mode": "",
            "Type": ""

        })

    return transactions