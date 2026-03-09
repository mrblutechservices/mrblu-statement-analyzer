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

        words = page.extract_words()

        text = " ".join([w["text"] for w in words])

        # ACCOUNT HOLDER (first big text)
        if words:
            info["Account Holder"] = words[0]["text"]

        # ACCOUNT NUMBER
        acc = re.search(r'Account\s*No\s*[:]*\s*(\d{10,})', text)
        if acc:
            info["Account Number"] = acc.group(1)

        # CUSTOMER ID
        cid = re.search(r'Customer\s*ID\s*[:]*\s*(\d+)', text)
        if cid:
            info["Customer ID"] = cid.group(1)

        # IFSC
        ifsc = re.search(r'UTIB[0-9A-Z]{7}', text)
        if ifsc:
            info["IFSC"] = ifsc.group()

        # EMAIL
        email = re.search(r'[\w\.-]+@[\w\.-]+', text)
        if email:
            info["Email"] = email.group()

        # MOBILE
        mobile = re.search(r'\d{4}608', text)
        if mobile:
            info["Mobile"] = mobile.group()

        # PERIOD
        period = re.search(r'From\s*:\s*([0-9\-]+)\s*To\s*:\s*([0-9\-]+)', text)
        if period:
            info["Period"] = period.group(1) + " to " + period.group(2)

    return info
