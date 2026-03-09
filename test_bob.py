import pdfplumber

pdf_path = "test.pdf"   # yahan apni BOB PDF ka naam likho

with pdfplumber.open(pdf_path) as pdf:

    page = pdf.pages[0]

    print("---- TEXT ----")
    print(page.extract_text())

    print("\n---- WORDS ----")
    print(page.extract_words()[:50])

    print("\n---- TABLES ----")
    print(page.extract_tables())