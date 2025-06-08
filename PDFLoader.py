import pdfplumber
from pathlib import Path

pdf_path = Path("docs/Eric_Abram_1.pdf")

all_text = []

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            all_text.append(text)

full_resume = "\n\n".join(all_text)
print(full_resume)
