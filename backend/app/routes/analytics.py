from fastapi import APIRouter
from backend.app.db.supabase import supabase
from typing import Any, Dict

router = APIRouter()


# ----------------------------
# Safe float conversion
# ----------------------------
def safe_float(val: Any) -> float:
    if isinstance(val, (int, float)):
        return float(val)

    if isinstance(val, str):
        try:
            return float(val.replace(",", "").strip())
        except:
            return 0.0

    return 0.0


# ----------------------------
# Vendor Spend
# ----------------------------
@router.get("/analytics/vendor-spend")
def vendor_spend() -> Dict[str, float]:
    response = supabase.table("invoices").select("*").execute()
    data = response.data or []

    result: Dict[str, float] = {}

    for inv in data:
        if not isinstance(inv, dict):
            continue

        raw_vendor = inv.get("vendor_name")

        vendor = (
            raw_vendor.strip()
            if isinstance(raw_vendor, str) and raw_vendor.strip()
            else "unknown"
        )

        total = safe_float(inv.get("total"))

        result[vendor] = result.get(vendor, 0.0) + total

    return result


# ----------------------------
# Product Spend
# ----------------------------
@router.get("/analytics/product-spend")
def product_spend() -> Dict[str, float]:
    response = supabase.table("invoices").select("*").execute()
    data = response.data or []

    result: Dict[str, float] = {}

    for inv in data:
        if not isinstance(inv, dict):
            continue

        items = inv.get("line_items")

        if not isinstance(items, list):
            continue

        for item in items:
            if not isinstance(item, dict):
                continue

            raw_name = item.get("product_name")

            name = (
                raw_name.strip()
                if isinstance(raw_name, str) and raw_name.strip()
                else "unknown"
            )

            price = safe_float(item.get("price"))
            quantity = safe_float(item.get("quantity"))

            value = price * quantity

            result[name] = result.get(name, 0.0) + value

    return result