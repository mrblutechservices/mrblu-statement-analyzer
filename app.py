from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
from parser import parse_pdf

app = Flask(__name__)

# Global storage for filtering
data_store = []


@app.route("/")
def home():
    return render_template("index.html")


# ---------------- UPLOAD ---------------- #

@app.route("/upload", methods=["POST"])
def upload():

    global data_store

    try:

        if "pdf" not in request.files:
            return jsonify({"error": "No file uploaded"})

        file = request.files["pdf"]

        if file.filename == "":
            return jsonify({"error": "Empty file name"})

        # Parse PDF
        result = parse_pdf(file)

        if isinstance(result, dict):

            data = result.get("transactions", [])
            info = result.get("info", {})

        else:

            data = result
            info = {}

        if not isinstance(data, list):
            data = []

        # Save data globally for filtering
        data_store = data

        # Extract party names
        names = list(
            set(
                [
                    r.get("Party", "Unknown")
                    for r in data
                    if isinstance(r, dict)
                ]
            )
        )

        names.sort()

        return jsonify(
            {
                "data": data,
                "names": names,
                "info": info,
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

        # Column filter
        if req.get("column") and req.get("value"):

            col = req["column"]

            if col in df.columns:
                df = df[
                    df[col]
                    .astype(str)
                    .str.contains(req["value"], case=False, na=False)
                ]

        # Amount filter
        if req.get("amount"):

            amt = str(req["amount"])

            df = df[
                df.apply(
                    lambda r: amt in str(r.values),
                    axis=1
                )
            ]

        # Type filter
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

    try:

        data = request.json

        df = pd.DataFrame(data)

        if df.empty:
            return jsonify({"error": "No data to export"})

        path = "result.xlsx"

        df.to_excel(path, index=False)

        return send_file(path, as_attachment=True)

    except Exception as e:

        return jsonify({"error": str(e)})


# ---------------- RUN SERVER ---------------- #

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)