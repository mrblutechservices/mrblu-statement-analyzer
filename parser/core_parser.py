from .bank_detector import detect_bank
from .axis_parser import parse_axis
from .axis_header import parse_axis_header
from .bob_parser import parse_bob
from .idfc_parser import parse_idfc
from .text_parser import parse_text
from .header_parser import extract_header_info

import io


def parse_pdf(file):

    print("=== PARSER START ===")

    pdf_bytes = file.read()

    stream = io.BytesIO(pdf_bytes)

    bank = detect_bank(stream)

    print("BANK DETECTED:", bank)

    transactions = []
    header_info = {}

    # -------- AXIS --------
    if bank == "Axis Bank":

        stream = io.BytesIO(pdf_bytes)
        transactions = parse_axis(stream)

        if not transactions:

            print("AXIS FALLBACK PARSER")

            stream = io.BytesIO(pdf_bytes)
            transactions = parse_text(stream)

        stream = io.BytesIO(pdf_bytes)
        header_info = parse_axis_header(stream)

    # -------- BOB --------
    elif bank == "Bank of Baroda":

        stream = io.BytesIO(pdf_bytes)
        transactions = parse_bob(stream)

        if not transactions:

            print("BOB FALLBACK PARSER")

            stream = io.BytesIO(pdf_bytes)
            transactions = parse_text(stream)

        stream = io.BytesIO(pdf_bytes)
        header_info = extract_header_info(stream)

    # -------- IDFC --------
    elif bank == "IDFC First Bank":

        stream = io.BytesIO(pdf_bytes)
        transactions = parse_idfc(stream)

        if not transactions:

            print("IDFC FALLBACK PARSER")

            stream = io.BytesIO(pdf_bytes)
            transactions = parse_text(stream)

        stream = io.BytesIO(pdf_bytes)
        header_info = extract_header_info(stream)

    # -------- UNKNOWN --------
    else:

        print("UNKNOWN BANK → UNIVERSAL PARSER")

        stream = io.BytesIO(pdf_bytes)
        transactions = parse_text(stream)

        stream = io.BytesIO(pdf_bytes)
        header_info = extract_header_info(stream)

    print("TOTAL TRANSACTIONS:", len(transactions))

    info = {"bank": bank}

    if isinstance(header_info, dict):
        info.update(header_info)

    return {

        "data": transactions,
        "info": info,
        "names": []

    }
