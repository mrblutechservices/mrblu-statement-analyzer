import pdfplumber
import re

def clean_amount(x):
    if not x:
        return 0.0
    x = str(x)
    x = x.replace(",", "")
    x = x.replace("CR", "")
    x = x.replace("Cr", "")
    x = x.replace("DR", "")
    x = x.replace("Dr", "")
    x = x.strip()
    try:
        return float(x)
    except:
        return 0.0


def find_column(headers, keywords):
    headers = [str(h).lower() for h in headers]
    for i, h in enumerate(headers):
        for key in keywords:
            if key in h:
                return i
    return None


def parse_table(file, bank):

    transactions = []

    with pdfplumber.open(file) as pdf:

        print("TOTAL PAGES:", len(pdf.pages))

        for page_number, page in enumerate(pdf.pages):

            print("READING PAGE:", page_number + 1)

            tables = page.extract_tables()

            if not tables:
                continue

            for table in tables:

                if not table or len(table) < 2:
                    continue

                header = [str(x).strip() for x in table[0]]

                date_col = find_column(header, ["date"])
                value_date_col = find_column(header, ["value"])
                desc_col = find_column(header, ["narration", "particular"])
                debit_col = find_column(header, ["withdrawal", "debit"])
                credit_col = find_column(header, ["deposit", "credit"])
                bal_col = find_column(header, ["balance"])

                if date_col is None or bal_col is None:
                    continue

                for row in table[1:]:

                    try:
                        date = row[date_col]
                        value_date = row[value_date_col] if value_date_col is not None else date
                        desc = row[desc_col] if desc_col is not None else ""

                        debit = clean_amount(row[debit_col]) if debit_col is not None else 0.0
                        credit = clean_amount(row[credit_col]) if credit_col is not None else 0.0
                        balance = clean_amount(row[bal_col]) if bal_col is not None else 0.0

                        if not date:
                            continue

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

                    except:
                        continue

    print("TOTAL TABLE ROWS:", len(transactions))
    return transactions