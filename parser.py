import pdfplumber
import re

date_pattern = r"\b(\d{2}[-/]\d{2}[-/]\d{4}|\d{2}-[A-Za-z]{3}-\d{2,4}|\d{2} [A-Za-z]{3} \d{4})\b"


def clean_amount(x):

    if not x:
        return ""

    x = str(x)

    x = x.replace(",", "")
    x = x.replace("CR", "")
    x = x.replace("DR", "")

    x = re.sub(r"[^\d\.]", "", x)

    return x.strip()


def detect_transaction_type(desc):

    desc = desc.upper()

    if "UPI" in desc:
        return "UPI"

    if "IMPS" in desc:
        return "IMPS"

    if "NEFT" in desc:
        return "NEFT"

    if "RTGS" in desc:
        return "RTGS"

    if "ATM" in desc:
        return "ATM"

    return "OTHER"


def extract_name(text):

    text = text.upper()

    patterns = [
        r'/([A-Z ]{4,})$',
        r'/([A-Z ]{4,})/',
        r'TO\s([A-Z ]{4,})',
        r'BY\s([A-Z ]{4,})'
    ]

    for p in patterns:

        m = re.search(p, text)

        if m:

            name = re.sub(r'[^A-Z ]', '', m.group(1))

            return name.title()

    return "Unknown"


# ---------------- PARSER ---------------- #

def parse_transactions(pdf):

    text = ""

    for page in pdf.pages:

        t = page.extract_text()

        if t:
            text += t + "\n"

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    transactions = []

    current = None

    for line in lines:

        date_match = re.search(date_pattern, line)

        if date_match:

            if current:
                transactions.append(current)

            date_val = date_match.group(0)

            current = {

                "Date": date_val,
                "Value_Date": "",
                "Description": line,
                "Cheque_No": "",
                "Debit": "",
                "Credit": "",
                "Balance": "",
                "Branch_Code": "",
                "Party": extract_name(line),
                "Mode": detect_transaction_type(line),
                "Type": detect_transaction_type(line)

            }

            nums = re.findall(r"\d[\d,]*\.\d{2}", line)

            if nums:

             amounts = [clean_amount(x) for x in nums]

             if "CR" in line.upper():
                 current["Credit"] = amounts[0]

             elif "DR" in line.upper():
                 current["Debit"] = amounts[0]

             elif len(amounts) == 1:
                 current["Debit"] = amounts[0]

             elif len(amounts) == 2:
                 current["Debit"] = amounts[0]
                 current["Balance"] = amounts[1]

             elif len(amounts) >= 3:
                 current["Debit"] = amounts[0]
                 current["Credit"] = amounts[1]
                 current["Balance"] = amounts[-1]

            if len(nums) == 1:

                current["Debit"] = clean_amount(nums[0])

            elif len(nums) >= 2:

                current["Debit"] = clean_amount(nums[0])
                current["Balance"] = clean_amount(nums[-1])

        else:

            if current:

                current["Description"] += " " + line

                nums = re.findall(r"\d[\d,]*\.\d{2}", line)

                if nums:

                    amount = clean_amount(nums[-1])

                    if "CR" in line.upper():

                        current["Credit"] = amount

                    else:

                        current["Debit"] = amount

    if current:
        transactions.append(current)

    return transactions


# ---------------- INFO ---------------- #

def extract_statement_info(pdf):

    info = {

        "bank": "",
        "account_holder": "",
        "account_number": "",
        "customer_id": "",
        "branch": "",
        "ifsc": "",
        "micr": "",
        "email": "",
        "mobile": "",
        "period": ""

    }

    text = ""

    for page in pdf.pages:

        t = page.extract_text()

        if t:
            text += t

    tu = text.upper()

    if "AXIS BANK" in tu:
        info["bank"] = "Axis Bank"

    elif "BANK OF BARODA" in tu:
        info["bank"] = "Bank of Baroda"

    elif "IDFC FIRST BANK" in tu:
        info["bank"] = "IDFC First Bank"

    m = re.search(r"ACCOUNT\s*(NO|NUMBER)\s*[:\-]?\s*([\dXx]+)", tu)

    if m:
        info["account_number"] = m.group(2)

    return info


# ---------------- MAIN ---------------- #

def parse_pdf(file):

    with pdfplumber.open(file) as pdf:

        info = extract_statement_info(pdf)

        transactions = parse_transactions(pdf)

    return {

        "transactions": transactions,
        "info": info

    }