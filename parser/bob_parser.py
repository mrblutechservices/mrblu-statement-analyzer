import pdfplumber
import re

date_pattern = r"\d{2}/\d{2}/\d{4}"


def clean_amount(x):
    if not x:
        return ""

    x = str(x)
    x = x.replace(",", "")
    x = x.replace("Cr", "")
    x = x.replace("CR", "")
    x = x.replace("Dr", "")
    x = x.replace("DR", "")

    return x.strip()


def detect_mode(desc):

    d = desc.upper()

    if "IMPS" in d:
        return "IMPS"
    if "UPI" in d:
        return "UPI"
    if "RTGS" in d:
        return "RTGS"
    if "NEFT" in d:
        return "NEFT"

    return "OTHER"


def extract_party(desc):

    d = desc.upper()

    ignore = [
        "IMPS","P2A","PAYMENT","PAYMENTBACK","RETURNPAYMENT",
        "EXTRAPAYMENT","PAID","TRANSFER","UPI"
    ]

    # IMPS logic
    if "IMPS" in d:

        parts = d.split("/")

        best = ""

        for p in parts:

            name = re.sub(r"[^A-Z ]", "", p).strip()

            if name and name not in ignore and len(name) > len(best):

                best = name

        if len(best) > 3:
            return best.title()

    # RTGS logic
    if "RTGS" in d:

        parts = d.split("-")

        best = ""

        for p in parts:

            name = re.sub(r"[^A-Z ]", "", p).strip()

            if len(name) > len(best):

                best = name

        if len(best) > 3:
            return best.title()

    return "Unknown"


def parse_bob(file):

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

    for line in lines:

        if re.match(date_pattern, line):

            if current:
                rows.append(current)

            current = line

        else:
            current += " " + line

    if current:
        rows.append(current)

    for row in rows:

        dates = re.findall(date_pattern, row)

        if len(dates) < 2:
            continue

        date = dates[0]
        value_date = dates[1]

        amounts = re.findall(r"\d[\d,]*\.\d{2}\s*(?:Cr|CR|Dr|DR)?", row)

        if len(amounts) < 2:
            continue

        balance = ""
        txn_amount = ""

        for a in amounts:

            if "CR" in a.upper() or "DR" in a.upper():

                balance = clean_amount(a)

        for a in amounts:

            if "CR" not in a.upper() and "DR" not in a.upper():

                txn_amount = clean_amount(a)
                break

        debit = ""
        credit = ""

        debit = ""
        credit = ""

        # If narration contains keywords like PaymentBack / Return etc → credit
        if float(balance) > float(txn_amount):

            credit = txn_amount
        else:
            debit = txn_amount

        narration = row

        for d in dates:
            narration = narration.replace(d, "")

        for a in amounts:
            narration = narration.replace(a, "")

        narration = narration.strip()

        transactions.append({

            "Date": date,
            "Value_Date": value_date,
            "Description": narration,
            "Cheque_No": "",
            "Debit": debit,
            "Credit": credit,
            "Balance": balance,
            "Branch_Code": "",
            "Party": extract_party(narration),
            "Mode": detect_mode(narration),
            "Type": detect_mode(narration)

        })

    return transactions