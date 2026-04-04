import requests
from backend.app.config import OCR_API_KEY


def extract_text(file_path):
    try:
        print(f"📄 OCR API processing: {file_path}")

        if not OCR_API_KEY:
            print("❌ OCR_API_KEY missing")
            return ""

        url = "https://api.ocr.space/parse/image"

        # ----------------------------
        # RETRY LOGIC (VERY IMPORTANT)
        # ----------------------------
        for attempt in range(2):
            try:
                with open(file_path, "rb") as f:
                    response = requests.post(
                        url,
                        files={"file": f},
                        data={
                            "apikey": OCR_API_KEY,
                            "language": "eng",
                            "OCREngine": 2,
                            "scale": True,
                            "detectOrientation": True,
                            "isTable": True  # 🔥 improves table OCR
                        },
                        timeout=30
                    )

                if response.status_code != 200:
                    print(f"❌ OCR HTTP error: {response.status_code}")
                    continue

                result = response.json()

                # ----------------------------
                # HANDLE OCR API ERROR
                # ----------------------------
                if result.get("IsErroredOnProcessing"):
                    print("❌ OCR API Error:", result.get("ErrorMessage"))
                    continue

                parsed_results = result.get("ParsedResults")

                if not parsed_results:
                    print("⚠️ No parsed results")
                    continue

                # ----------------------------
                # EXTRACT TEXT
                # ----------------------------
                text = "\n".join(
                    item.get("ParsedText", "")
                    for item in parsed_results
                )

                # ----------------------------
                # CLEAN TEXT (CRITICAL)
                # ----------------------------
                text = text.replace("\r", "")

                text = "\n".join(
                    line.strip()
                    for line in text.split("\n")
                    if line.strip()
                )

                # ----------------------------
                # VALIDATION
                # ----------------------------
                if len(text) < 20:
                    print("⚠️ OCR text too small, retrying...")
                    continue

                print(f"✅ OCR success | Length: {len(text)}")
                return text

            except requests.exceptions.Timeout:
                print("⚠️ OCR timeout, retrying...")

        # ----------------------------
        # FINAL FAILURE
        # ----------------------------
        print("❌ OCR failed after retries")
        return ""

    except Exception as e:
        print("❌ OCR Exception:", e)
        return ""