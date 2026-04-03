from PIL import Image
import pytesseract
from pdf2image import convert_from_path


def extract_text(file_path):
    try:
        text = ""

        if file_path.lower().endswith(".pdf"):
            images = convert_from_path(file_path)

            for img in images:
                text += pytesseract.image_to_string(img)

        else:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)

        return text.strip()

    except Exception as e:
        print("OCR Error:", e)
        return ""