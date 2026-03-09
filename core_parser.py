from .bank_detector import detect_bank
from .header_parser import extract_header_info

from .axis_parser import parse_axis
from .axis_header import parse_axis_header
from .bob_parser import parse_bob
from .idfc_parser import parse_idfc
from .sbi_parser import parse_sbi
from .idbi_parser import parse_idbi
from .boi_parser import parse_boi
from .iob_parser import parse_iob

import io

def parse_pdf(file):

    # read pdf once into memory
    pdf_bytes = file.read()

    # create fresh stream
    stream = io.BytesIO(pdf_bytes)

    bank = detect_bank(stream)
    print("DETECTED BANK:", bank)

    stream.seek(0)

    # fallback detection
    if bank == "Unknown":
        print("Bank not detected")
        
        return {
            "data": [],
            "info": {"bank": "Unknown"},
            "names": []

        }

    # header parsing
    stream = io.BytesIO(pdf_bytes)
    header_info = extract_header_info(stream)

    transactions = []

    if bank == "Axis Bank":

        stream = io.BytesIO(pdf_bytes)
        transactions = parse_axis(stream)

        stream = io.BytesIO(pdf_bytes)
        header_info = parse_axis_header(stream)

        print("HEADER DATA:", header_info)

    elif bank == "Bank of Baroda":

        print("ENTERED BOB PARSER")

        stream = io.BytesIO(pdf_bytes)
        transactions = parse_bob(stream)

        print("BOB RESULT:", len(transactions))

    elif bank == "IDFC First Bank":

        stream = io.BytesIO(pdf_bytes)
        transactions = parse_idfc(stream)

    elif bank == "SBI":

        stream = io.BytesIO(pdf_bytes)
        transactions = parse_sbi(stream)

    elif bank == "IDBI":

        stream = io.BytesIO(pdf_bytes)
        transactions = parse_idbi(stream)

    elif bank == "Bank of India":

        stream = io.BytesIO(pdf_bytes)
        transactions = parse_boi(stream)

    elif bank == "Indian Overseas Bank":

        stream = io.BytesIO(pdf_bytes)
        transactions = parse_iob(stream)

    print("BANK DETECTED:", bank)
    print("TRANSACTIONS FOUND:", len(transactions))

    info = {"bank": bank}

    if isinstance(header_info, dict):
     info.update(header_info)


    print("FINAL BANK:", bank)
    print("TOTAL TRANSACTIONS:", len(transactions))
    
    return {
    "data": transactions if transactions else [],
    "info": info,
    "names": []
}