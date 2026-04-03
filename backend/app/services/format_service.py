from backend.app.db.supabase import supabase
from typing import Optional, Dict, Any


# ----------------------------
# Normalize Vendor
# ----------------------------
def normalize_vendor_name(vendor: str) -> str:
    return vendor.lower().strip()


# ----------------------------
# Extract STRUCTURE
# ----------------------------
def extract_structure(data: Dict[str, Any]) -> Dict[str, Any]:
    line_items = data.get("line_items")

    return {
        "keys": list(data.keys()),
        "has_line_items": isinstance(line_items, list) and len(line_items) > 0,
        "currency": data.get("currency"),
    }


# ----------------------------
# Save Format (only if good)
# ----------------------------
def save_format(data: Dict[str, Any]) -> None:
    vendor = data.get("vendor_name")

    if not vendor or vendor == "unknown":
        return

    vendor = normalize_vendor_name(vendor)
    structure = extract_structure(data)

    existing = supabase.table("invoice_formats") \
        .select("vendor_name") \
        .eq("vendor_name", vendor) \
        .execute()

    if not existing.data and data.get("confidence_score", 0) > 0.75:
        supabase.table("invoice_formats").insert({
            "vendor_name": vendor,
            "sample_structure": structure
        }).execute()


# ----------------------------
# Get Format
# ----------------------------
def get_vendor_format(vendor: str) -> Optional[Dict[str, Any]]:
    if not vendor:
        return None

    vendor = normalize_vendor_name(vendor)

    res = supabase.table("invoice_formats") \
        .select("sample_structure") \
        .eq("vendor_name", vendor) \
        .execute()

    if res.data and isinstance(res.data, list):
        row = res.data[0]

        if isinstance(row, dict):
            structure = row.get("sample_structure")

            if isinstance(structure, dict):
                return structure

    return None