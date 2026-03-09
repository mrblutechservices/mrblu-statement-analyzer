import pdfplumber
import re
from .schemas import BANK_SCHEMAS

date_pattern = r"\b(\d{2}[-/]\d{2}[-/]\d{4}|\d{2}-[A-Za-z]{3}-\d{2,4}|\d{2} [A-Za-z]{3} \d{4})\b"

def find_column(headers, keyword):

    headers = [str(h).lower() for h in headers]

    keyword = keyword.lower()

    for i, h in enumerate(headers):

        if keyword in h:
            return i

    return None


def clean_amount(x):

    if not x:
        return ""

    x = str(x)

    x = x.replace(",", "")
    x = x.replace("CR", "")
    x = x.replace("DR", "")

    return x.strip()


def parse_table(file, bank):

    schema = BANK_SCHEMAS.get(bank)

    if not schema:
        return []

    transactions = []

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            tables = page.extract_tables()

            for table in tables:

                if not table:
                    continue

                header = [str(x).strip() for x in table[0]]

                try:

                    date_col = find_column(header, schema["date"])
                    desc_col = find_column(header, schema["description"])
                    debit_col = find_column(header, schema["debit"])
                    credit_col = find_column(header, schema["credit"])
                    bal_col = find_column(header, schema["balance"])

                except:
                    continue

                for row in table[1:]:

                    if not row:
                        continue


                    row_text = " ".join([str(x) if x else "" for x in row])


                    if not re.search(date_pattern, row_text):
                        continue


                    date_val = row[date_col] if date_col is not None else ""
                    desc = row[desc_col] if desc_col is not None else ""
                    debit = row[debit_col] if debit_col is not None else ""
                    credit = row[credit_col] if credit_col is not None else ""
                    balance = row[bal_col] if bal_col is not None else ""

                    transactions.append({

                        "Date": date_val,
                        "Value_Date": "",
                        "Description": desc,
                        "Cheque_No": "",
                        "Debit": clean_amount(debit),
                        "Credit": clean_amount(credit),
                        "Balance": clean_amount(balance),
                        "Branch_Code": "",
                        "Party": desc,
                        "Mode": "",
                        "Type": ""

                    })

    return transactions