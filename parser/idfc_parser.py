import pdfplumber
import re


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


def parse_idfc(file):

    transactions = []

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            tables = page.extract_tables()

            for table in tables:

                if not table or len(table) < 2:
                    continue

                header = [str(h).upper() for h in table[0]]

                date_col = None
                value_date_col = None
                desc_col = None
                balance_col = None

                for i, h in enumerate(header):
                    if "TRANSACTION DATE" in h:
                        date_col = i
                    elif "VALUE DATE" in h:
                        value_date_col = i
                    elif "PARTICULAR" in h:
                        desc_col = i
                    elif "BALANCE" in h:
                        balance_col = i

                if date_col is None or balance_col is None:
                    continue

                for row in table[1:]:

                    try:
                        date = row[date_col]
                        value_date = row[value_date_col] if value_date_col is not None else date
                        desc = row[desc_col] if desc_col is not None else ""
                        balance = clean_amount(row[balance_col])

                        if not date:
                            continue

                        transactions.append({
                            "Date": date,
                            "Value_Date": value_date,
                            "Description": desc,
                            "Cheque_No": "",
                            "Debit": 0.0,
                            "Credit": 0.0,
                            "Balance": balance,
                            "Branch_Code": "",
                            "Party": "",
                            "Mode": "",
                            "Type": ""
                        })

                    except:
                        continue

    print("IDFC PARSED:", len(transactions))
    return transactions