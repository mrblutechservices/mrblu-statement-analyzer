import pdfplumber
import re

date_pattern = r"\b(\d{2}[-/]\d{2}[-/]\d{4}|\d{2}-[A-Za-z]{3}-\d{2,4}|\d{2} [A-Za-z]{3} \d{4})\b"


def clean_text(text):

    if not text:
        return ""

    text = str(text)

    text = text.replace("\n", " ")
    text = text.replace("  ", " ")

    return text.strip()


def extract_party(description):

    if "UPI" in description:

        parts = description.split("/")

        if len(parts) >= 4:
            return parts[3]

    return "Unknown"


def extract_mode(description):

    if "UPI" in description:
        return "UPI"

    if "IMPS" in description:
        return "IMPS"

    if "NEFT" in description:
        return "NEFT"

    if "ATM" in description:
        return "ATM"

    return "Other"


def parse_axis(file):

    transactions = []

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            table = page.extract_table()

            if not table:
                continue

            for row in table:

                if not row:
                    continue

                row_text = " ".join([str(x) for x in row if x])

                if not re.search(date_pattern, row_text):
                    continue

                date = row[0] if len(row) > 0 else ""

                cheque = row[1] if len(row) > 1 else ""

                description = clean_text(row[2] if len(row) > 2 else "")

                debit = row[3] if len(row) > 3 else ""
                credit = row[4] if len(row) > 4 else ""
                balance = row[5] if len(row) > 5 else ""

                branch = row[6] if len(row) > 6 else ""

                party = extract_party(description)

                mode = extract_mode(description)

                transaction = {
                    "Date": date,
                    "Value_Date": "",
                    "Description": description,
                    "Cheque_No": cheque,
                    "Debit": debit,
                    "Credit": credit,
                    "Balance": balance,
                    "Branch_Code": branch,
                    "Party": party,
                    "Mode": mode,
                    "Type": "",
                }

                transactions.append(transaction)

    return transactions