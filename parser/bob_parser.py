import pdfplumber
import re

date_pattern = r"\d{2}/\d{2}/\d{4}"


def parse_amount_with_sign(x):
    if not x:
        return None

    x = str(x).replace(",", "").strip()

    sign = 1
    if x.endswith("Dr") or x.endswith("DR"):
        sign = -1

    x = x.replace("Cr", "").replace("CR", "")
    x = x.replace("Dr", "").replace("DR", "")

    try:
        return float(x) * sign
    except:
        return None


def parse_bob(file):

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

        numbers = re.findall(r"\d[\d,]*\.\d{2}\s?(Cr|Dr)?", line)

        # Extract full amounts including Cr/Dr
        amounts = re.findall(r"\d[\d,]*\.\d{2}\s?(?:Cr|Dr)?", line)

        if len(amounts) == 0:
            continue

        balance = parse_amount_with_sign(amounts[-1])

        desc = line
        desc = re.sub(date_pattern, "", desc)
        desc = re.sub(r"\d[\d,]*\.\d{2}\s?(Cr|Dr)?", "", desc)
        desc = re.sub(r"\s+", " ", desc).strip()

        transactions.append({
            "Date": date,
            "Value_Date": date,
            "Description": desc,
            "Cheque_No": "",
            "Debit": 0,
            "Credit": 0,
            "Balance": balance,
            "Branch_Code": "",
            "Party": "",
            "Mode": "",
            "Type": ""
        })

    # IMPORTANT — Reverse order (oldest first)
    transactions = list(reversed(transactions))

    print("BOB PARSED:", len(transactions))
    return transactions
