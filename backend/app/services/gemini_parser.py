import json
import re
from typing import Dict, Any, List, Optional
from google import genai
from backend.app.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


# ----------------------------
# SAFE JSON PARSER
# ----------------------------
def safe_json_load(text: str) -> Dict[str, Any]:
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, dict):
                return data
        except:
            pass

    return {}


# ----------------------------
# REGEX FALLBACK
# ----------------------------
def extract_with_regex(ocr_text: str) -> Dict[str, Any]:
    data = {}

    invoice_no = re.search(r"(Invoice\s*No[:\s]*)([A-Za-z0-9\-]+)", ocr_text, re.I)
    if invoice_no:
        data["invoice_number"] = invoice_no.group(2)

    date = re.search(r"(\d{2}[/-]\d{2}[/-]\d{4})", ocr_text)
    if date:
        data["invoice_date"] = date.group(1)

    total = re.search(r"(Total\s*[:₹\s]*)(\d+\.?\d*)", ocr_text, re.I)
    if total:
        data["total"] = float(total.group(2))

    lines = ocr_text.split("\n")
    if lines:
        data["vendor_name"] = lines[0].strip()

    return data


# ----------------------------
# SIMPLE LINE ITEM EXTRACTION
# ----------------------------
def extract_line_items(ocr_text: str) -> List[Dict[str, Any]]:
    items = []

    pattern = re.findall(r"([A-Za-z0-9\s]+)\s+(\d+)\s+₹?(\d+\.?\d*)", ocr_text)

    for match in pattern:
        items.append({
            "product_name": match[0].strip(),
            "quantity": int(match[1]),
            "price": float(match[2])
        })

    return items


# ----------------------------
# MAIN PARSER (LLM + FALLBACK)
# ----------------------------
def parse_invoice(
    ocr_text: str,
    hint: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:

    try:
        prompt = f"""
Extract structured invoice JSON.

Return ONLY JSON:
{{
  "vendor_name": "",
  "invoice_number": "",
  "invoice_date": "",
  "total": 0,
  "currency": "INR",
  "line_items": []
}}

OCR TEXT:
{ocr_text[:3000]}
"""

        if hint:
            prompt += f"\nUse this structure: {json.dumps(hint)}"

        # ----------------------------
        # TRY LLM
        # ----------------------------
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            if not response or not response.text:
                raise Exception("Empty response")

            llm_data = safe_json_load(response.text)

        except Exception as llm_error:
            print("🔥 LLM FAILED → Using fallback:", llm_error)
            llm_data = {}

        # ----------------------------
        # REGEX FALLBACK
        # ----------------------------
        regex_data = extract_with_regex(ocr_text)

        parsed = {
            "vendor_name": llm_data.get("vendor_name") or regex_data.get("vendor_name", "unknown"),
            "invoice_number": llm_data.get("invoice_number") or regex_data.get("invoice_number", ""),
            "invoice_date": llm_data.get("invoice_date") or regex_data.get("invoice_date", ""),
            "total": llm_data.get("total") or regex_data.get("total", 0),
            "currency": "INR",
        }

        # ----------------------------
        # LINE ITEMS
        # ----------------------------
        line_items = llm_data.get("line_items")

        if not isinstance(line_items, list) or not line_items:
            line_items = extract_line_items(ocr_text)

        if not line_items:
            line_items = [{
                "product_name": "Detected Item",
                "quantity": 1,
                "price": parsed["total"]
            }]

        parsed["line_items"] = line_items

        # ----------------------------
        # CONFIDENCE SCORE
        # ----------------------------
        score = sum([
            bool(parsed["vendor_name"]),
            bool(parsed["invoice_number"]),
            bool(parsed["invoice_date"]),
            bool(parsed["total"]),
            bool(parsed["line_items"])
        ]) * 0.2

        parsed["confidence_score"] = round(score, 2)

        return parsed

    except Exception as e:
        return {
            "vendor_name": "unknown",
            "invoice_number": "",
            "invoice_date": "",
            "total": 0,
            "currency": "INR",
            "line_items": [{
                "product_name": "Error Item",
                "quantity": 1,
                "price": 0
            }],
            "confidence_score": 0.3,
            "error": str(e)
        }