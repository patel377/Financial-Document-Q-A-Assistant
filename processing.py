# processing.py
import pdfplumber
import pandas as pd
import pytesseract
from PIL import Image
import io

def extract_from_pdf(path, ocr=False):
    """
    Returns a list of chunks: [{ "text": "...", "meta": {"page": i, "filename": ...}}]
    """
    results = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            # try to extract simple tables
            tables = page.extract_tables()
            table_texts = []
            for t in tables:
                try:
                    df = pd.DataFrame(t[1:], columns=t[0])
                    table_texts.append(df.to_csv(index=False))
                except Exception:
                    pass
            full_text = text + "\n\n" + ("\n\n".join(table_texts) if table_texts else "")
            if (not full_text.strip()) and ocr:
                # fallback OCR
                im = page.to_image(resolution=300).original
                pil = Image.fromarray(im)
                ocr_text = pytesseract.image_to_string(pil)
                full_text = ocr_text
            results.append({"text": full_text, "meta": {"page": i}})
    return results

def extract_from_excel(path):
    """
    Read all sheets and produce a text blob per sheet.
    """
    xls = pd.ExcelFile(path)
    results = []
    for sheet in xls.sheet_names:
        df = xls.parse(sheet)
        # convert to simple text representation
        txt = df.to_csv(index=False)
        results.append({"text": txt, "meta": {"sheet": sheet}})
    return results
