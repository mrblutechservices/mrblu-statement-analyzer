import pdfplumber
import re


def parse_axis_header(file):

    info = {
        "Account Holder": "",
        "Account Number": "",
        "Branch": "",
        "IFSC": "",
        "Mobile": "",
        "Email": "",
        "Period": "",
        "Customer ID": ""
    }

    with pdfplumber.open(file) as pdf:

        page = pdf.pages[0]

        text = page.extract_text()

        if not text:
            return info

        text = text.upper()

        # Account number
        acc = re.search(r"\b\d{10,18}\b", text)
        if acc:
            info["Account Number"] = acc.group()

        # IFSC
        ifsc = re.search(r"UTIB[0-9A-Z]{7}", text)
        if ifsc:
            info["IFSC"] = ifsc.group()

        # Email
        email = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text)
        if email:
            info["Email"] = email.group()

        # Period
        period = re.search(r"\d{2}-\d{2}-\d{4}\s+TO\s+\d{2}-\d{2}-\d{4}", text)
        if period:
            info["Period"] = period.group()

    return info