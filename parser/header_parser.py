import pdfplumber
import re


def extract_header_info(file):

    info = {
        "Bank": "",
        "Account Holder": "",
        "Account Number": "",
        "Branch": "",
        "IFSC": "",
        "Mobile": "",
        "Email": "",
        "Period": ""
    }

    text = ""

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages[:2]:

            t = page.extract_text()

            if t:
                text += t + "\n"

    text_upper = text.upper()

    # BANK DETECTION
    if "IDFC FIRST BANK" in text_upper:
        info["Bank"] = "IDFC First Bank"

    elif "AXIS BANK" in text_upper:
        info["Bank"] = "Axis Bank"

    elif "BANK OF BARODA" in text_upper:
        info["Bank"] = "Bank of Baroda"

    lines = text.split("\n")

    for line in lines:

        l = line.strip()

        acc = re.search(r"\b\d{10,18}\b", l)

        if acc and info["Account Number"] == "":
            info["Account Number"] = acc.group()

        ifsc = re.search(r"[A-Z]{4}0[A-Z0-9]{6}", l)

        if ifsc:
            info["IFSC"] = ifsc.group()

        email = re.search(r"[\w\.-]+@[\w\.-]+", l)

        if email:
            info["Email"] = email.group()

    return info