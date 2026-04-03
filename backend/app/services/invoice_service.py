from backend.app.services.ocr import extract_text
from backend.app.services.gemini_parser import parse_invoice
from backend.app.services.format_service import get_vendor_format, save_format

from backend.app.utils.json_cleaner import clean_json
from backend.app.utils.vendor_normalizer import normalize_vendor
from backend.app.db.supabase import supabase
from backend.app.schemas.invoice import InvoiceCreate

from typing import Dict, Any
import os


ALLOWED_COLUMNS = {
    "vendor_name",
    "invoice_number",
    "invoice_date",
    "due_date",
    "total",
    "currency",
    "confidence_score",
    "is_duplicate",
    "line_items",
    "highlights",
    "parsed_data",
    "raw_text"
}


# ----------------------------
# SAFE FLOAT
# ----------------------------
def safe_float(val):
    try:
        return float(str(val).replace(",", ""))
    except:
        return 0.0


# ----------------------------
# 🔥 FIX: NORMALIZE LINE ITEMS
# ----------------------------
def normalize_line_items(line_items):
    normalized = []

    for item in line_items or []:
        if not isinstance(item, dict):
            continue

        product_name = (
            item.get("product_name")
            or item.get("description")
            or "Unknown"
        )

        price = (
            item.get("price")
            or item.get("amount")
            or item.get("unit_price")
            or 0
        )

        normalized.append({
            "product_name": product_name,
            "quantity": item.get("quantity", 1),
            "price": safe_float(price),
            "amount": safe_float(item.get("amount") or price),
        })

    return normalized


# ----------------------------
# MAIN PROCESS FUNCTION
# ----------------------------
def process_invoice(file_path: str) -> Dict[str, Any]:
    try:
        text = extract_text(file_path)

        if not text:
            return {"status": "error", "message": "OCR failed"}

        # ----------------------------
        # FIRST PARSE
        # ----------------------------
        raw = parse_invoice(text)

        if "error" in raw:
            raise Exception(raw["error"])

        data = clean_json(raw)

        if not isinstance(data, dict):
            raise Exception("Invalid parsed data")

        # ----------------------------
        # NORMALIZE VENDOR
        # ----------------------------
        data["vendor_name"] = normalize_vendor(data.get("vendor_name"))

        # ----------------------------
        # FORMAT REFINEMENT
        # ----------------------------
        format_hint = get_vendor_format(data["vendor_name"])

        if isinstance(format_hint, dict):
            refined = parse_invoice(text, hint=format_hint)

            if "error" not in refined:
                improved = clean_json(refined)
                if isinstance(improved, dict):
                    data = improved
                    data["confidence_score"] = max(
                        data.get("confidence_score", 0), 0.9
                    )

        # ----------------------------
        # DEFAULTS
        # ----------------------------
        data.setdefault("total", 0)
        data.setdefault("currency", "INR")
        data.setdefault("confidence_score", 0.7)
        data.setdefault("line_items", [])

        # ----------------------------
        # 🔥 FIX: NORMALIZE PRODUCTS
        # ----------------------------
        data["line_items"] = normalize_line_items(data.get("line_items"))

        # ----------------------------
        # VALIDATE SCHEMA
        # ----------------------------
        data = InvoiceCreate(**data).dict()

        # ----------------------------
        # DUPLICATE CHECK
        # ----------------------------
        existing = supabase.table("invoices") \
            .select("invoice_number, vendor_name, total") \
            .eq("vendor_name", data["vendor_name"]) \
            .execute().data or []

        existing_set = {
            (
                inv.get("invoice_number"),
                inv.get("vendor_name"),
                safe_float(inv.get("total"))
            )
            for inv in existing if isinstance(inv, dict)
        }

        current = (
            data.get("invoice_number"),
            data.get("vendor_name"),
            safe_float(data.get("total"))
        )

        is_duplicate = current in existing_set
        data["is_duplicate"] = is_duplicate

        # ----------------------------
        # 🔥 FIX: STOP DUPLICATE INSERT
        # ----------------------------
        if is_duplicate:
            return {
                "status": "duplicate",
                "message": "Invoice already exists",
                "data": data
            }

        # ----------------------------
        # HIGHLIGHTS
        # ----------------------------
        highlights = {}
        for k, v in data.items():
            if isinstance(v, (str, int, float)) and str(v).lower() in text.lower():
                highlights[k] = v

        data["highlights"] = highlights

        # ----------------------------
        # STORE RAW DATA
        # ----------------------------
        temp = data.copy()
        temp.pop("parsed_data", None)

        data["parsed_data"] = temp
        data["raw_text"] = text

        # ----------------------------
        # FILTER DB COLUMNS
        # ----------------------------
        filtered = {k: v for k, v in data.items() if k in ALLOWED_COLUMNS}

        # ----------------------------
        # SAVE FORMAT (LEARNING SYSTEM)
        # ----------------------------
        save_format(filtered)

        # ----------------------------
        # INSERT INTO DB
        # ----------------------------
        res = supabase.table("invoices").insert(filtered).execute()

        if res.data is None:
            raise Exception("DB insert failed")

        return {"status": "success", "data": filtered}

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


# ----------------------------
# FORMAT STORAGE
# ----------------------------
def save_format(data):
    vendor = data.get("vendor_name")

    if not vendor:
        return

    existing = supabase.table("invoice_formats") \
        .select("*") \
        .eq("vendor_name", vendor) \
        .execute()

    if not existing.data:
        supabase.table("invoice_formats").insert({
            "vendor_name": vendor,
            "sample_structure": data
        }).execute()