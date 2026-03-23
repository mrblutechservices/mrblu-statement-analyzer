import pdfplumber
import re

date_pattern = r"\d{2}[-/]\d{2}[-/]\d{4}"


def clean_amount(x):
    if not x:
        return 0.0
    x = str(x)
    x = x.replace(",", "")
    x = x.replace("CR", "")
    x = x.replace("DR", "")
    x = x.strip()
    try:
        return float(x)
    except:
        return 0.0


def parse_text(file):

    transactions = []

    with pdfplumber.open(file) as pdf:

        full_text = ""

        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    lines = full_text.split("\n")

    for line in lines:

        if not re.search(date_pattern, line):
            continue

        date = re.search(date_pattern, line).group()

        # Extract all numbers
        numbers = re.findall(r"\d[\d,]*\.\d{2}", line)

        if len(numbers) < 2:
            continue

        numbers = [clean_amount(n) for n in numbers]

        # Last number = Balance
        balance = numbers[-1]

        # Second last = Amount
        amount = numbers[-2]

        debit = 0
        credit = 0

        if "CR" in line.upper():
            credit = amount
        elif "DR" in line.upper():
            debit = amount
        else:
            # Use balance difference logic later
            debit = 0
            credit = 0

        # Clean description
        desc = line
        desc = re.sub(date_pattern, "", desc)
        desc = re.sub(r"\d[\d,]*\.\d{2}", "", desc)
        desc = re.sub(r"CR|DR", "", desc)
        desc = re.sub(r"\s+", " ", desc).strip()

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

    print("TEXT PARSED:", len(transactions))
    return transactions