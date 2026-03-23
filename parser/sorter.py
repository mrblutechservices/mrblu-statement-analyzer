from datetime import datetime


def parse_date(date_str):
    if not date_str:
        return None

    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d-%b-%Y",
        "%d/%m/%y",
        "%d-%m-%y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(str(date_str).strip(), fmt)
        except:
            continue

    return None


def sort_transactions(transactions):

    for i, t in enumerate(transactions):
        t["parsed_date"] = parse_date(t.get("Date"))
        t["parsed_value_date"] = parse_date(t.get("Value_Date"))
        t["_index"] = i  # preserve original order

    # Remove rows without date
    transactions = [t for t in transactions if t["parsed_date"]]

    # Sort by Date → Value Date → Original Index
    transactions.sort(
        key=lambda x: (
            x["parsed_date"] or datetime.min,
            x["parsed_value_date"] or datetime.min,
            x["_index"]
        )
    )

    # Cleanup temp fields
    for t in transactions:
        t.pop("parsed_date", None)
        t.pop("parsed_value_date", None)
        t.pop("_index", None)

    return transactions