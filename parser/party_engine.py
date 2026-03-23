import re

def clean_name(name):
    if not name:
        return "Unknown"

    name = str(name).upper()
    name = re.sub(r"[^A-Z ]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()

    if len(name) < 3:
        return "Unknown"

    return name.title()


def extract_party(description):

    if not description:
        return "Unknown"

    desc = description.upper()

    # Remove numbers
    desc = re.sub(r"\d+", " ", desc)

    # Remove keywords
    remove_words = [
        "IMPS","UPI","RTGS","NEFT","ATM",
        "TRANSFER","PAYMENT","PAYMENTBACK",
        "EXTRAPAYMENT","CHARGE","REF",
        "BANK","FROM","TO","BY","INB",
        "DR","CR"
    ]

    for w in remove_words:
        desc = desc.replace(w, " ")

    desc = re.sub(r"[^A-Z ]", " ", desc)
    desc = re.sub(r"\s+", " ", desc).strip()

    words = desc.split()

    if not words:
        return "Unknown"

    if len(words) >= 3:
        party = " ".join(words[-3:])
    elif len(words) == 2:
        party = " ".join(words)
    else:
        party = words[0]

    return clean_name(party)


def apply_party_engine(transactions):

    for t in transactions:
        party = t.get("Party", "")

        if not party or party == "Unknown":
            desc = t.get("Description", "")
            t["Party"] = extract_party(desc)

    return transactions