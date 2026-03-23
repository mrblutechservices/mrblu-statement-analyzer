import pdfplumber


def detect_bank(file):

    text = ""

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages[:2]:

            t = page.extract_text()

            if t:
                text += t + "\n"

    text = text.upper()

    # AXIS FIRST
    if "AXIS BANK" in text or "UTIB" in text:
        return "Axis Bank"

    # IDFC
    if "IDFC FIRST BANK" in text :
        return "IDFC First Bank"

    # BANK OF BARODA
    if "BANK OF BARODA" in text or "XOMB" in text:
        return "Bank of Baroda"

    return "Unknown"