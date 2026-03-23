def clean_number(val):
    if val is None:
        return None
    val = str(val)
    val = val.replace(",", "").replace("Cr", "").replace("Dr", "")
    val = val.replace("CR", "").replace("DR", "").strip()
    try:
        return float(val)
    except:
        return None


def transaction_engine(transactions, bank):

    # Clean numbers
    for t in transactions:
        t["Balance"] = clean_number(t.get("Balance"))
        t["Debit"] = clean_number(t.get("Debit"))
        t["Credit"] = clean_number(t.get("Credit"))

    # Remove rows without balance
    transactions = [t for t in transactions if t["Balance"] is not None]

    if len(transactions) == 0:
        return transactions

    cleaned_transactions = []

    # Try to detect opening balance
    opening_balance = None

    first_desc = str(transactions[0].get("Description", "")).lower()

    if "opening" in first_desc:
        opening_balance = transactions[0]["Balance"]
        transactions = transactions[1:]
    else:
        # If first row has no debit/credit → treat as opening
        if not transactions[0].get("Debit") and not transactions[0].get("Credit"):
            opening_balance = transactions[0]["Balance"]
            transactions = transactions[1:]
        else:
            # Assume opening = 0
            opening_balance = 0

    prev_balance = opening_balance

    for t in transactions:

        balance = t["Balance"]
        debit = t["Debit"] or 0
        credit = t["Credit"] or 0

        diff = round(balance - prev_balance, 2)

        if diff == 0:
            prev_balance = balance
            continue

        # If bank already gave debit/credit use it
        if debit > 0 and credit == 0:
            t["Type"] = "Debit"

        elif credit > 0 and debit == 0:
            t["Type"] = "Credit"

        else:
            # Calculate from balance difference
            if diff > 0:
                t["Credit"] = abs(diff)
                t["Debit"] = 0
                t["Type"] = "Credit"
            else:
                t["Debit"] = abs(diff)
                t["Credit"] = 0
                t["Type"] = "Debit"

        prev_balance = balance
        cleaned_transactions.append(t)

    return cleaned_transactions