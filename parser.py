import pdfplumber
import pandas as pd
import re
import numpy as np

date_pattern = r"\d{2}[-/ ]?[A-Za-z]{3}[-/ ]?\d{4}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}"

COLUMN_MAP = {
    "date": ["date", "tran date", "transaction date"],
    "value_date": ["value date"],
    "description": ["description", "particulars", "narration", "remarks"],
    "debit": ["debit", "withdrawal", "dr"],
    "credit": ["credit", "deposit", "cr"],
    "balance": ["balance"],
    "cheque_no": ["cheque no", "chq no", "cheque"],
    "branch_code": ["init br", "branch code"]
}


def find_column(headers, names):
    headers = [str(h).lower() for h in headers]
    for name in names:
        for i, h in enumerate(headers):
            if name in h:
                return i
    return None


def detect_transaction_type(desc):
    if not desc:
        return ""

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
    if "TPFT" in desc:
        return "TRANSFER"
    if "MOB" in desc:
        return "MOBILE"
    if "CHARGE" in desc or "CHRG" in desc:
        return "BANK CHARGE"
    if "CASH" in desc:
        return "CASH"
    if "TRANSFER" in desc:
        return "TRANSFER"

    return "OTHER"


def extract_name(text):
    if not text:
        return "Unknown"

    text = str(text).upper()

    patterns = [
        r'/([A-Z ]{4,})$',
        r'/([A-Z ]{4,})/',
        r'UPI.*?/([A-Z ]{4,})',
        r'IMPS.*?/([A-Z ]{4,})',
        r'NEFT.*?/([A-Z ]{4,})',
        r'TO\s([A-Z ]{4,})',
        r'BY\s([A-Z ]{4,})'
    ]

    for p in patterns:
        m = re.search(p, text)
        if m:
            name = m.group(1)
            name = re.sub(r'[^A-Z ]', '', name)
            return name.strip()

    return "Unknown"


def clean_amount(x):
    if not x:
        return ""

    x = str(x)

    x = x.replace(",", "")
    x = x.replace("CR", "")
    x = x.replace("Cr", "")
    x = x.replace("DR", "")
    x = x.replace("Dr", "")

    return x.strip()


def clean_description(text):
    if not text:
        return ""

    text = str(text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'/Payment.*', '', text, flags=re.I)
    text = re.sub(r'/Paymen.*', '', text, flags=re.I)

    return text.strip()


# -------- TABLE PARSER --------

def parse_table(file):
    transactions = []

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            tables = page.extract_tables()

            for table in tables:

                if not table:
                    continue

                header = [str(h).strip() for h in table[0]]

                date_col = find_column(header, COLUMN_MAP["date"])
                value_col = find_column(header, COLUMN_MAP["value_date"])
                desc_col = find_column(header, COLUMN_MAP["description"])
                debit_col = find_column(header, COLUMN_MAP["debit"])
                credit_col = find_column(header, COLUMN_MAP["credit"])
                bal_col = find_column(header, COLUMN_MAP["balance"])
                chq_col = find_column(header, COLUMN_MAP["cheque_no"])
                branch_col = find_column(header, COLUMN_MAP["branch_code"])

                current = None

                for r in table[1:]:

                    if not any(r):
                        continue

                    row = [str(x) if x else "" for x in r]

                    if date_col is not None and re.search(date_pattern, row[date_col]):

                        if current:
                            transactions.append(current)

                        current = {
                            "Date": row[date_col],
                            "Value_Date": row[value_col] if value_col is not None else "",
                            "Description": row[desc_col] if desc_col is not None else "",
                            "Cheque_No": row[chq_col] if chq_col is not None else "",
                            "Debit": clean_amount(row[debit_col]) if debit_col is not None else "",
                            "Credit": clean_amount(row[credit_col]) if credit_col is not None else "",
                            "Balance": clean_amount(row[bal_col]) if bal_col is not None else "",
                            "Branch_Code": row[branch_col] if branch_col is not None else ""
                        }

                        # detect numbers inside description (BOB style)
                        nums = re.findall(r"\d[\d,]*\.\d{2}\s*(?:CR|DR|Cr|Dr)?", current["Description"])

                        if nums:
                            amounts = [clean_amount(n) for n in nums]

                            # if only one amount → debit
                            if len(amounts) == 1:
                                if current["Debit"] == "" and current["Credit"] == "":
                                    current["Debit"] = amounts[0]

                            # if two amounts → debit + balance
                            elif len(amounts) >= 2:

                                if current["Debit"] == "" and current["Credit"] == "":
                                    current["Debit"] = amounts[0]
                                    current["Balance"] = amounts[-1]

                    else:

                        if current:
                            current["Description"] += " " + " ".join(row)

                if current:
                    transactions.append(current)

    if not transactions:
        return None

    df = pd.DataFrame(transactions)

    df = df.replace({np.nan: ""})
    df = df.fillna("")

    df["Description"] = df["Description"].apply(clean_description)

    # -------- BOB multiline amount extraction --------
    def extract_amounts(desc):
        nums = re.findall(r"\d[\d,]*\.\d{2}\s*(?:CR|DR|Cr|Dr)?", desc)

        debit = ""
        credit = ""
        balance = ""

        if nums:

            amounts = [clean_amount(x) for x in nums]

            if len(amounts) == 1:
                debit = amounts[0]

            elif len(amounts) >= 2:
                debit = amounts[0]
                balance = amounts[-1]

        return pd.Series([debit, credit, balance])

    df[["Debit", "Credit", "Balance"]] = df.apply(
        lambda r: extract_amounts(r["Description"])
        if r["Debit"] == "" and r["Credit"] == "" else
        pd.Series([r["Debit"], r["Credit"], r["Balance"]]),
        axis=1
    )

    df = df[~df["Description"].str.contains(
        "OPENING BALANCE|ACCOUNT STATEMENT|STATEMENT OF|REGISTERED OFFICE",
        case=False,
        na=False
    )]

    df["Party"] = df.astype(str).apply(
        lambda r: extract_name(" ".join(r)),
        axis=1
    )

    df["Type"] = df["Description"].apply(detect_transaction_type)

    return df.to_dict(orient="records")


# -------- TEXT PARSER --------

def parse_text(file):
    rows = []

    with pdfplumber.open(file) as pdf:

        text = ""

        for page in pdf.pages:

            t = page.extract_text()

            if t:
                text += t + "\n"

    lines = text.split("\n")

    current = None

    for line in lines:

        if re.search(date_pattern, line):

            if current:
                rows.append(current)

            date_match = re.search(date_pattern, line)

            date_val = date_match.group(0)

            rest = line.replace(date_val, "").strip()

            current = {
                "Date": date_val,
                "Value_Date": "",
                "Description": rest,
                "Cheque_No": "",
                "Debit": "",
                "Credit": "",
                "Balance": "",
                "Branch_Code": "",
                "Party": "",
                "Type": ""
            }

        elif current:

            nums = re.findall(r"\d[\d,]*\.\d{2}", line)

            if len(nums) >= 1:

                if current["Debit"] == "":
                    current["Debit"] = clean_amount(nums[0])

                current["Balance"] = clean_amount(nums[-1])

            else:

                current["Description"] += " " + line.strip()

    if current:
        rows.append(current)

    df = pd.DataFrame(rows)

    if df.empty:
        return []

    df = df.fillna("")
    df = df.replace({np.nan: ""})

    df["Description"] = df["Description"].apply(clean_description)

    df = df[~df["Description"].str.contains(
        "OPENING BALANCE|ACCOUNT STATEMENT|STATEMENT OF",
        case=False,
        na=False
    )]

    df["Party"] = df.astype(str).apply(
        lambda r: extract_name(" ".join(r)),
        axis=1
    )

    df["Type"] = df["Description"].apply(detect_transaction_type)

    return df.to_dict(orient="records")


# -------- STATEMENT INFO --------

def extract_statement_info(file):
    info = {
        "bank": "",
        "account_holder": "",
        "account_number": "",
        "customer_id": "",
        "branch": "",
        "ifsc": "",
        "micr": "",
        "mobile": "",
        "email": "",
        "period": ""
    }

    with pdfplumber.open(file) as pdf:

        text = ""

        for page in pdf.pages:

            t = page.extract_text()

            if t:
                text += t + "\n"

    text = text.upper()

    if "AXIS BANK" in text:
        info["bank"] = "Axis Bank"

    elif "BANK OF BARODA" in text:
        info["bank"] = "Bank of Baroda"

    elif "IDFC FIRST BANK" in text:
        info["bank"] = "IDFC First Bank"

    m = re.search(r"CUSTOMER NAME\s*[:\-]?\s*([A-Z ]+)", text)

    if m:
        info["account_holder"] = m.group(1).strip()

    m = re.search(r"ACCOUNT\s*NO\s*[:\-]?\s*([0-9X]+)", text)

    if m:
        info["account_number"] = m.group(1)

    m = re.search(r"CUSTOMER\s*ID\s*[:\-]?\s*([A-Z0-9]+)", text)

    if m:
        info["customer_id"] = m.group(1)

    m = re.search(r"BRANCH\s*NAME\s*[:\-]?\s*([A-Z ]+)", text)

    if m:
        info["branch"] = m.group(1)

    m = re.search(r"\b[A-Z]{4}0[A-Z0-9]{6}\b", text)

    if m:
        info["ifsc"] = m.group(0)

    m = re.search(r"MICR\s*CODE\s*[:\-]?\s*([0-9]+)", text)

    if m:
        info["micr"] = m.group(1)

    m = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text)

    if m:
        info["email"] = m.group(0)

    m = re.search(r"FROM\s*[0-9\/\-]+\s*TO\s*[0-9\/\-]+", text)

    if m:
        info["period"] = m.group(0)

    return info


# -------- NORMALIZE --------

def normalize_transactions(data):
    final = []

    for r in data:

        row = {
            "Date": r.get("Date", ""),
            "Value_Date": r.get("Value_Date", ""),
            "Party": r.get("Party", "Unknown"),
            "Description": clean_description(r.get("Description", "")),
            "Mode": detect_transaction_type(r.get("Description", "")),
            "Type": r.get("Type", ""),
            "Cheque_No": r.get("Cheque_No", ""),
            "Debit": clean_amount(r.get("Debit", "")),
            "Credit": clean_amount(r.get("Credit", "")),
            "Balance": clean_amount(r.get("Balance", "")),
            "Branch_Code": r.get("Branch_Code", "")
        }

        final.append(row)

    return final


# -------- MAIN --------

def parse_pdf(file):
    info = extract_statement_info(file)

    try:

        data = parse_table(file)

        if data and len(data) > 5:

            data = normalize_transactions(data)

            return {
                "transactions": data,
                "info": info
            }

    except:
        pass

    data = parse_text(file)

    data = normalize_transactions(data)

    return {
        "transactions": data,
        "info": info
    }
