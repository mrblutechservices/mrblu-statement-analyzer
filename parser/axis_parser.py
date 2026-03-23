import pdfplumber
import re


def clean_amount(x):
    if not x:
        return 0.0
    x = str(x)
    x = x.replace(",", "").strip()
    try:
        return float(x)
    except:
        return 0.0


def parse_axis(file):

    transactions = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:

            tables = page.extract_tables()

            for table in tables:

                for row in table:

                    if not row or len(row) < 6:
                        continue

                    date = str(row[0]).strip()

                    # Skip header
                    if "Tran" in date or "Date" in date:
                        continue

                    # Skip opening balance row
                    if "OPENING" in str(row[2]).upper():
                        continue

                    desc = str(row[2]).strip()

                    debit = clean_amount(row[3])
                    credit = clean_amount(row[4])
                    balance = clean_amount(row[5])

                    if not date or balance == 0:
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

    print("AXIS TABLE PARSED:", len(transactions))
    return transactions