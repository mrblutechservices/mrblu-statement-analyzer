import pdfplumber
import re


def extract_header_info(file):

    info = {
        "Account Holder": "",
        "Account Number": "",
        "Branch": "",
        "IFSC": "",
        "Mobile": "",
        "Email": "",
        "Period": ""
    }

    with pdfplumber.open(file) as pdf:

        page = pdf.pages[0]

        text = page.extract_text()

        if not text:
            return info

        lines = text.split("\n")

        for line in lines:

            l = line.strip()

            # ACCOUNT NUMBER
            if "Account No" in l or "Account Number" in l:

                acc = re.search(r'\d{10,}', l)

                if acc:
                    info["Account Number"] = acc.group()

            # IFSC
            if "IFSC" in l:

                ifsc = re.search(r'[A-Z]{4}0[A-Z0-9]{6}', l)

                if ifsc:
                    info["IFSC"] = ifsc.group()

            # EMAIL
            email = re.search(r'[\w\.-]+@[\w\.-]+', l)

            if email:
                info["Email"] = email.group()

            # MOBILE
            mobile = re.search(r'\b[6-9]\d{9}\b', l)

            if mobile:
                info["Mobile"] = mobile.group()

            # PERIOD
            if "Statement Period" in l or "Period" in l:

                info["Period"] = l.split(":")[-1].strip()

            # BRANCH
            if "Branch" in l:

                info["Branch"] = l.split(":")[-1].strip()

        # ACCOUNT HOLDER (Axis me address ke upar hota hai)

        for i in range(len(lines)):

            if "Account No" in lines[i]:

                if i > 0:
                    info["Account Holder"] = lines[i-1].strip()

                break

    return info