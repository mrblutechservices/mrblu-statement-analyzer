import pdfplumber
import re

date_pattern = r"\d{2}/\d{2}/\d{4}"


def clean_amount(x):
    if not x:
        return 0.0
    x = str(x)
    x = x.replace(",", "")
    x = x.replace("Cr", "")
    x = x.replace("Dr", "")
    x = x.strip()
    try:
        return float(x)
    except:
        return 0.0


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

        if re.search(date_pattern, line):

            parts = line.split()

            if len(parts) < 5:
                continue

            date = parts[0]
            value_date = parts[1]

            numbers = re.findall(r"\d[\d,]*\.\d{2}", line)

            if len(numbers) < 2:
                continue

            numbers = [clean_amount(x) for x in numbers]

            if len(numbers) == 2:
                amount = numbers[0]
                balance = numbers[1]

                if "CR" in line.upper():
                    credit = amount
                    debit = 0
                else:
                    debit = amount
                    credit = 0
            else:
                debit = numbers[0]
                credit = numbers[1]
                balance = numbers[-1]

            desc = line
            desc = re.sub(date_pattern, "", desc)
            desc = re.sub(r"\d[\d,]*\.\d{2}", "", desc)
            desc = re.sub(r"CR|DR", "", desc)
            desc = re.sub(r"\s+", " ", desc).strip()

            transactions.append({
                "Date": date,
                "Value_Date": value_date,
                "Description": desc,
                "Cheque_No": "",
                "Debit": debit,
                "Credit": credit,
                "Balance": balance,
                "Branch_Code": "",
                "Party": "",
                "Mode": "",
                "Type": "",
            })

    print("BOB TEXT ROWS:", len(transactions))
    return transactions