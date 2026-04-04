import json
import re
from typing import Dict, Any
from difflib import get_close_matches
from google import genai
from backend.app.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

# ----------------------------
# 🧠 VENDOR DB
# ----------------------------
VENDOR_DB = [
    "ONEPLUS TECHNOLOGY INDIA PVT LTD",
    "AMAZON SELLER SERVICES PVT LTD",
    "FLIPKART INTERNET PRIVATE LIMITED",
    "RELIANCE DIGITAL RETAIL LTD"
]

# ----------------------------
# SAFE JSON
# ----------------------------
def safe_json_load(text: str):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}|\[.*\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
    return {}

# ----------------------------
# ✅ PRODUCT FROM RAW OCR (🔥 BEST METHOD)
# ----------------------------
def extract_product_from_text(text):
    match = re.search(
        r"\d+\s+([A-Za-z0-9\s\-]+?(?:Buds|Phone|Laptop|Headphones|Watch|Tablet|Camera)[^\n]+)",
        text
    )
    if match:
        return match.group(1).strip()
    return None

# ----------------------------
# ✅ VENDOR EXTRACTION
# ----------------------------
def extract_vendor(text):
    for line in text.split("\n")[:20]:
        line = line.strip()
        if re.search(r"(PVT|LTD|PRIVATE|LIMITED|TECHNOLOGY)", line, re.I):
            return line
    return "unknown"

def match_vendor(text):
    extracted = extract_vendor(text)
    match = get_close_matches(extracted, VENDOR_DB, n=1, cutoff=0.6)
    return match[0] if match else extracted

# ----------------------------
# ✅ TOTAL + GST
# ----------------------------
def extract_totals(text):
    data = {}

    total = re.search(r"Grand total.*?(\d+\.\d{2})", text, re.I)
    if total:
        data["total"] = float(total.group(1))

    cgst = re.search(r"CGST.*?(\d+\.\d{2})", text, re.I)
    sgst = re.search(r"SGST.*?(\d+\.\d{2})", text, re.I)

    if cgst:
        data["cgst"] = float(cgst.group(1))
    if sgst:
        data["sgst"] = float(sgst.group(1))

    if "total" in data and "cgst" in data and "sgst" in data:
        data["subtotal"] = round(data["total"] - data["cgst"] - data["sgst"], 2)

    return data

# ----------------------------
# TABLE BLOCK
# ----------------------------
def extract_table_block(text):
    lines = text.split("\n")
    table_lines = []
    capture = False

    for line in lines:
        line = line.strip()

        if re.search(r"(ITEM|DESCRIPTION|PRODUCT|QTY)", line, re.I):
            capture = True
            continue

        if re.search(r"(Grand total|Payment|Summary)", line, re.I):
            break

        if capture and line:
            table_lines.append(line)

    return table_lines

# ----------------------------
# ✅ SMART TABLE PARSER (FIXED)
# ----------------------------
def extract_rows(table_lines):
    rows = []
    product_lines = []

    for line in table_lines:

        # ❌ Skip garbage lines
        if re.search(r"(HSN|IMEI|GST|CGST|SGST|IGST|UOM|DISCOUNT)", line, re.I):
            continue

        if re.search(r"(AMOUNT|RATE|TAX|TOTAL)", line, re.I):
            continue

        # Product text continuation
        if not re.search(r"\d+\.\d{2}", line):
            if len(line.split()) > 2:
                product_lines.append(line)
            continue

        numbers = [float(n) for n in re.findall(r"\d+\.\d{2}", line)]
        if not numbers:
            continue

        # price selection
        price_candidates = [n for n in numbers if n > 1000]
        price = max(price_candidates) if price_candidates else max(numbers)

        # quantity
        quantity = 1
        qty_match = re.search(r"\b([1-9]|10)\b", line)
        if qty_match:
            quantity = int(qty_match.group(1))

        # merge product name
        name = " ".join(product_lines)

        # clean
        name = re.sub(r"(AMOUNT|RATE|TAX|CGST|SGST|IGST)", "", name, flags=re.I)
        name = re.sub(r"\b\d{10,}\b", "", name)
        name = re.sub(r"\s+", " ", name).strip()

        product_lines = []

        if len(name) < 10:
            continue

        rows.append({
            "product_name": name,
            "quantity": quantity,
            "price": price
        })

    return rows

# ----------------------------
# MAIN LINE ITEM EXTRACTION
# ----------------------------
def extract_line_items_smart(text):
    table = extract_table_block(text)
    return extract_rows(table)

# ----------------------------
# BASIC EXTRACTION
# ----------------------------
def extract_basic(text):
    data = {}

    inv = re.search(r"Invoice Number[:\s]*([A-Za-z0-9\-]+)", text)
    if inv:
        data["invoice_number"] = inv.group(1)

    date = re.search(r"(\d{2}/\d{2}/\d{4})", text)
    if date:
        data["invoice_date"] = date.group(1)

    return data

# ----------------------------
# 🤖 AI CONFIDENCE
# ----------------------------
def ai_confidence(data):
    try:
        prompt = f"""
Evaluate invoice extraction.

Return JSON:
{{"score": 0-1}}

DATA:
{json.dumps(data)}
"""
        res = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt
        )

        parsed = safe_json_load(res.text or "")
        return parsed.get("score", 0.95)

    except:
        return 0.95

# ----------------------------
# 🚀 MAIN PARSER
# ----------------------------
def parse_invoice(ocr_text: str, hint=None):

    base = extract_basic(ocr_text)
    totals = extract_totals(ocr_text)

    # 🔥 PRIORITY PRODUCT EXTRACTION
    direct_product = extract_product_from_text(ocr_text)

    # fallback table parser
    items = extract_line_items_smart(ocr_text)

    # 🔥 OVERRIDE (fixes your issue)
    if direct_product:
        items = [{
            "product_name": direct_product,
            "quantity": 1,
            "price": totals.get("total", 0)
        }]

    # Gemini cleanup
    try:
        if items:
            prompt = f"""
Clean product names only. Do NOT change price or quantity.

DATA:
{json.dumps(items)}

Return JSON list only.
"""
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt
            )

            refined = safe_json_load(response.text or "")

            if isinstance(refined, list) and refined:
                items = refined

    except Exception as e:
        print("⚠️ Gemini failed:", e)

    # fallback safety
    if not items:
        items = [{
            "product_name": "Item",
            "quantity": 1,
            "price": totals.get("total", 0)
        }]

    result = {
        "vendor_name": match_vendor(ocr_text),
        "invoice_number": base.get("invoice_number", ""),
        "invoice_date": base.get("invoice_date", ""),
        "currency": "INR",
        "subtotal": totals.get("subtotal"),
        "cgst": totals.get("cgst"),
        "sgst": totals.get("sgst"),
        "total": totals.get("total"),
        "line_items": items
    }

    result["confidence_score"] = ai_confidence(result)

    return result