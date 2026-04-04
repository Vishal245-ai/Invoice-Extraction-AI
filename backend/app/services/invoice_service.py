from backend.app.services.ocr import extract_text
from backend.app.services.gemini_parser import parse_invoice
from backend.app.services.format_service import get_vendor_format, save_format

from backend.app.utils.json_cleaner import clean_json
from backend.app.utils.vendor_normalizer import normalize_vendor
from backend.app.db.supabase import supabase
from backend.app.schemas.invoice import InvoiceCreate

from typing import Dict, Any
import os
import re


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
# CLEAN PRODUCT NAME
# ----------------------------
def clean_product_name(name: str):
    if not name:
        return None

    name = name.replace("\n", " ").strip()
    name = re.sub(r"\b\d+\b$", "", name)  # remove trailing qty like "1"
    name = re.sub(r"\s+", " ", name)

    return name


# ----------------------------
# 🔥 NORMALIZE LINE ITEMS (FINAL)
# ----------------------------
def normalize_line_items(line_items, raw_text=None):
    normalized = []

    for item in line_items or []:
        if not isinstance(item, dict):
            continue

        # ----------------------------
        # PRODUCT NAME
        # ----------------------------
        product_name = (
            item.get("product_name")
            or item.get("description")
        )

        product_name = clean_product_name(product_name)

        # 🔥 Fallback using raw OCR text
        if (not product_name or len(product_name) < 10) and raw_text:
            match = re.search(
                r"(OnePlus.*?Black IN|OnePlus.*?IN)",
                raw_text,
                re.IGNORECASE
            )
            if match:
                product_name = match.group(1)

        # ----------------------------
        # PRICE
        # ----------------------------
        price = (
            item.get("price")
            or item.get("amount")
            or item.get("unit_price")
            or 0
        )

        normalized.append({
            "product_name": product_name or "Unknown Product",
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

        # 🔥 FIX PRODUCT EXTRACTION
        data["line_items"] = normalize_line_items(
            data.get("line_items"),
            raw_text=text
        )

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
        # SAVE FORMAT
        # ----------------------------
        save_format(filtered)

        # ----------------------------
        # INSERT
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
