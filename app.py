from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
import re

from parser.core_parser import parse_pdf

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

data_store = []
info_store = {}

# ---------------- NAME NORMALIZATION ---------------- #

def normalize_name(name):

    if not name:
        return "Unknown"

    name = str(name).upper()

    name = re.sub(r"[^A-Z ]", "", name)

    name = name.strip()

    if name == "":
        return "Unknown"

    return name


# ---------------- PARTY FALLBACK ---------------- #

def extract_party_from_desc(desc):

    if not desc:
        return "Unknown"

    d = desc.upper()

    tokens = re.split(r"[\/\-\s]", d)

    ignore = [
        "UPI","IMPS","RTGS","NEFT","ATM",
        "CR","DR","PAYMENT","TRANSFER",
        "CHARGE","DEBIT","CREDIT","BANK",
        "REF","TO","FROM"
    ]

    best = ""

    for t in tokens:

        name = re.sub(r"[^A-Z ]", "", t).strip()

        if name in ignore:
            continue

        if len(name) > len(best):
            best = name

    if len(best) > 3:
        return best.title()

    return "Unknown"


# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- UPLOAD ---------------- #

@app.route("/upload", methods=["POST"])
def upload():

    global data_store, info_store

    try:

        if "pdf" not in request.files:
            return jsonify({"error": "No file uploaded"})

        file = request.files["pdf"]

        if file.filename == "":
            return jsonify({"error": "Empty file name"})

        result = parse_pdf(file)

        if isinstance(result, dict):

            data = result.get("data", [])
            info = result.get("info", {})

        else:

            data = result
            info = {}

        if not isinstance(data, list):
            data = []

        fixed_data = []

        sr = 1

        for row in data:

            if not isinstance(row, dict):
                continue

            party = row.get("Party", "")

            if not party or party == "Unknown":

                desc = row.get("Description", "")

                party = extract_party_from_desc(desc)

            party = normalize_name(party)

            new_row = {

                "Sr_No": sr,

                "Date": row.get("Date",""),
                "Value_Date": row.get("Value_Date",""),
                "Party": party,
                "Mode": row.get("Mode",""),
                "Type": row.get("Type",""),
                "Cheque_No": row.get("Cheque_No",""),
                "Debit": row.get("Debit",""),
                "Credit": row.get("Credit",""),
                "Balance": row.get("Balance",""),
                "Branch_Code": row.get("Branch_Code",""),
                "Description": row.get("Description","")

            }

            fixed_data.append(new_row)

            sr += 1

        data_store = fixed_data
        info_store = info

        names = list(
            set(
                [
                    r.get("Party", "Unknown")
                    for r in fixed_data
                    if isinstance(r, dict)
                ]
            )
        )

        names.sort()

        return jsonify(
            {
                "data": fixed_data,
                "names": names,
                "info": info_store,
            }
        )

    except Exception as e:

        return jsonify({"error": str(e)})


# ---------------- FILTER ---------------- #

@app.route("/filter", methods=["POST"])
def filter_data():

    global data_store

    try:

        req = request.json

        df = pd.DataFrame(data_store)

        if df.empty:
            return jsonify([])

        if req.get("column") and req.get("value"):

            col = req["column"]

            if col in df.columns:

                df = df[
                    df[col]
                    .astype(str)
                    .str.contains(req["value"], case=False, na=False)
                ]

        if req.get("amount"):

            amt = str(req["amount"])

            df = df[
                df.apply(
                    lambda r: amt in str(r.values),
                    axis=1
                )
            ]

        if req.get("type") and req["type"] != "":

            t = req["type"].lower()

            df = df[
                df.apply(
                    lambda r: t in str(r.values).lower(),
                    axis=1
                )
            ]

        return jsonify(df.to_dict(orient="records"))

    except Exception as e:

        return jsonify({"error": str(e)})


# ---------------- EXPORT EXCEL ---------------- #

@app.route("/export_excel", methods=["POST"])
def export_excel():

    global data_store

    try:

        req = request.json

        if req and isinstance(req, list) and len(req) > 0:

            df = pd.DataFrame(req)

        else:

            df = pd.DataFrame(data_store)

        if df.empty:
            return jsonify({"error": "No data to export"})

        cols = [
            "Sr_No",
            "Date",
            "Value_Date",
            "Party",
            "Description",
            "Mode",
            "Type",
            "Cheque_No",
            "Debit",
            "Credit",
            "Balance",
            "Branch_Code"
        ]

        for c in cols:
            if c not in df.columns:
                df[c] = ""

        df = df[cols]

        for col in ["Debit", "Credit", "Balance"]:

            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
            )

        path = "result.xlsx"

        df.to_excel(path, index=False)

        return send_file(path, as_attachment=True)

    except Exception as e:

        return jsonify({"error": str(e)})


# ---------------- RUN SERVER ---------------- #

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
