import pdfplumber
import re

date_pattern = r"\b(\d{2}[-/]\d{2}[-/]\d{4}|\d{2}-[A-Za-z]{3}-\d{4})\b"


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

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    rows = []
    current = ""

    # -------- BUILD MULTI LINE ROWS -------- #

    for line in lines:

        if re.search(date_pattern, line):

            if current:
                rows.append(current)

            current = line

        else:

            current += " " + line

    if current:
        rows.append(current)

    # -------- PARSE ROWS -------- #

    for row in rows:

        date_match = re.search(date_pattern, row)

        if not date_match:
            continue

        nums = re.findall(r"\d[\d,]*\.\d{2}", row)

        # MUST HAVE AMOUNT + BALANCE
        if len(nums) < 2:
            continue

        date = date_match.group()

        nums = [clean_amount(x) for x in nums]

        debit = ""
        credit = ""
        balance = ""

        if len(nums) == 2:

            amount = nums[0]
            balance = nums[1]

            if "CR" in row.upper():
                credit = amount
            else:
                debit = amount

        elif len(nums) >= 3:

            debit = nums[0]
            credit = nums[1]
            balance = nums[-1]

        desc = row.replace(date, "").strip()

        # SKIP HEADER TEXT
        skip_words = [
            "STATEMENT",
            "ACCOUNT STATEMENT",
            "OPENING BALANCE",
            "CLOSING BALANCE",
            "TRAN DATE",
            "VALUE DATE",
            "NARRATION",
            "PARTICULARS"
        ]

        if any(x in desc.upper() for x in skip_words):
            continue

        transactions.append({

            "Date": date,
            "Value_Date": date,
            "Description": desc,
            "Cheque_No": "",
            "Debit": debit,
            "Credit": credit,
            "Balance": balance,
            "Branch_Code": "",
            "Party": "",
            "Mode": "",
            "Type": ""

        })

    print("UNIVERSAL PARSER:", len(transactions))

    return transactions
