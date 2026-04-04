from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import os

# ✅ Set tesseract path (REQUIRED for Render)
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


def extract_text(file_path):
    try:
        print(f"📄 Processing file: {file_path}")

        text = ""

        # ----------------------------
        # PDF → IMAGE → OCR
        # ----------------------------
        if file_path.lower().endswith(".pdf"):
            images = convert_from_path(
                file_path,
                poppler_path="/usr/bin"  # ✅ REQUIRED for Render
            )

            print(f"📑 Pages detected: {len(images)}")

            for i, img in enumerate(images):
                page_text = pytesseract.image_to_string(img)
                print(f"🧾 Page {i+1} OCR length:", len(page_text))

                text += page_text + "\n"

        # ----------------------------
        # IMAGE → OCR
        # ----------------------------
        else:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)

        # ----------------------------
        # VALIDATION
        # ----------------------------
        if not text.strip():
            print("⚠️ OCR returned empty text")
            return ""

        return text.strip()

    except Exception as e:
        print("❌ OCR Error:", str(e))
        return ""