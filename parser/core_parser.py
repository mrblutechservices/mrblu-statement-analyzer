from .axis_parser import parse_axis
from .bob_parser import parse_bob
from .idfc_parser import parse_idfc
from .table_parser import parse_table
from .text_parser import parse_text
from .transaction_engine import transaction_engine
from .party_engine import apply_party_engine
from .header_parser import extract_header_info
from .sorter import sort_transactions

import io


def normalize_transactions(transactions):

    cleaned = []

    for t in transactions:
        if not isinstance(t, dict):
            continue

        row = {
            "Date": t.get("Date",""),
            "Value_Date": t.get("Value_Date",""),
            "Description": t.get("Description",""),
            "Cheque_No": t.get("Cheque_No",""),
            "Debit": t.get("Debit",0),
            "Credit": t.get("Credit",0),
            "Balance": t.get("Balance",0),
            "Branch_Code": t.get("Branch_Code",""),
            "Party": t.get("Party",""),
            "Mode": t.get("Mode",""),
            "Type": t.get("Type",""),
        }

        cleaned.append(row)

    return cleaned


def parse_pdf(file, selected_bank):

    pdf_bytes = file.read()
    transactions = []
    header_info = {}

    # ---------------- BANK PARSER ---------------- #

    if selected_bank == "axis":
        bank = "Axis Bank"
        stream = io.BytesIO(pdf_bytes)
        transactions = parse_axis(stream)

    elif selected_bank == "idfc":
        bank = "IDFC First Bank"
        stream = io.BytesIO(pdf_bytes)
        transactions = parse_table(stream, bank)

    elif selected_bank == "bob":
        bank = "Bank of Baroda"
        stream = io.BytesIO(pdf_bytes)
        transactions = parse_bob(stream)

    else:
        bank = "Other"
        stream = io.BytesIO(pdf_bytes)
        transactions = parse_text(stream)

    print("TOTAL PARSED:", len(transactions))

    # Normalize
    transactions = normalize_transactions(transactions)

    # ---------------- SORT ---------------- #
    transactions = sort_transactions(transactions)

    # ---------------- ENGINE ---------------- #
    transactions = transaction_engine(transactions, bank)

    # ---------------- PARTY ---------------- #
    transactions = apply_party_engine(transactions)

    # ---------------- HEADER ---------------- #
    stream = io.BytesIO(pdf_bytes)
    header_info = extract_header_info(stream)

    info = {}
    if isinstance(header_info, dict):
        info.update(header_info)

    info["bank"] = bank

    return {
        "data": transactions,
        "info": info,
        "names": []
    }