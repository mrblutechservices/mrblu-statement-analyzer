import pdfplumber


def detect_bank(file):

    text = ""

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            t = page.extract_text()

            if t:
                text += t.upper()

    print("TEXT SAMPLE:", text[:500])

    # AXIS (check first)
    if (
        "AXIS BANK" in text
        or "STATEMENT OF AXIS" in text
        or "UTIB" in text
    ):
        return "Axis Bank"

    # Bank of Baroda
    if (
        "BANK OF BARODA" in text
        or "BARODA" in text
        or "BARB0" in text
    ):
        return "Bank of Baroda"

    # IDFC
    if "IDFC FIRST BANK" in text or "IDFC" in text:
        return "IDFC First Bank"

    # SBI
    if "STATE BANK OF INDIA" in text or "SBIN" in text:
        return "SBI"

    # BOI
    if "BANK OF INDIA" in text:
        return "Bank of India"

    # IOB
    if "INDIAN OVERSEAS BANK" in text:
        return "Indian Overseas Bank"

    # IDBI
    if "IDBI BANK" in text:
        return "IDBI"

    return "Unknown"