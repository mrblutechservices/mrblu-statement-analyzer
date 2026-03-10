import pdfplumber
import re

date_pattern = r"\b\d{2}-[A-Za-z]{3}-\d{4}\b"


def detect_mode(desc):

    d = desc.upper()

    if "UPI" in d:
        return "UPI"

    if "IMPS" in d:
        return "IMPS"

    if "RTGS" in d:
        return "RTGS"

    if "NEFT" in d:
        return "NEFT"

    if "ATM" in d:
        return "ATM"

    return "Other"


def extract_party(desc):

    if not desc:
        return "Unknown"

    d = desc.upper()

    tokens = re.split(r"[\/\-]", d)

    ignore = [
        "UPI","IMPS","RTGS","NEFT","ATM",
        "CR","DR","PAYMENT","TRANSFER",
        "CHARGE","DEBIT","CREDIT"
    ]

    best = ""

    for t in tokens:

        name = re.sub(r"[^A-Z ]", "", t).strip()

        if name in ignore:
            continue

        if len(name) > len(best):
            best = name

    if len(best) > 3:
        return best.title()

    return "Unknown"



def parse_idfc(file):

    transactions = []

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            if not text:
                continue

            lines = text.split("\n")

            for line in lines:

                if not re.search(date_pattern, line):
                    continue

                date_match = re.search(date_pattern, line)

                date = date_match.group()

                nums = re.findall(r"\d[\d,]*\.\d{2}", line)

                debit = ""
                credit = ""
                balance = ""

                nums = [x.replace(",", "") for x in nums]

                if len(nums) == 2:

                    amount = nums[0]
                    balance = nums[1]

                    if "CR" in line.upper():
                        credit = amount
                    else:
                        debit = amount

                elif len(nums) >= 3:

                    debit = nums[0]
                    credit = nums[1]
                    balance = nums[2]


                desc = line.replace(date, "").strip()

                party = extract_party(desc)

                mode = detect_mode(desc)

                transactions.append({

                    "Date": date,
                    "Value_Date": date,
                    "Description": desc,
                    "Cheque_No": "",
                    "Debit": debit,
                    "Credit": credit,
                    "Balance": balance,
                    "Branch_Code": "",
                    "Party": party,
                    "Mode": mode,
                    "Type": mode

                })


    return transactions
