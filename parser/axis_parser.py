import pdfplumber
import re

date_pattern = r"\d{2}[-/]\d{2}[-/]\d{4}"


def clean_amount(x):

    if not x:
        return ""

    x = str(x)

    x = x.replace(",", "")

    return x.strip()


def parse_axis(file):

    transactions = []

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            tables = page.extract_tables()

            if not tables:
                continue

            for table in tables:

                for row in table:

                    if not row:
                        continue

                    row_text = " ".join([str(x) for x in row if x])

                    if not re.search(date_pattern, row_text):
                        continue

                    date = re.search(date_pattern, row_text).group()

                    narration = row[2] if len(row) > 2 else ""

                    debit = ""
                    credit = ""
                    balance = ""

                    try:

                        debit = clean_amount(row[3])
                        credit = clean_amount(row[4])
                        balance = clean_amount(row[5])

                    except:
                        pass

                    transactions.append({

                        "Date": date,
                        "Value_Date": date,
                        "Description": narration,
                        "Cheque_No": "",
                        "Debit": debit,
                        "Credit": credit,
                        "Balance": balance,
                        "Branch_Code": "",
                        "Party": "",
                        "Mode": "",
                        "Type": ""

                    })

    return transactions
