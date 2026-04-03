from fastapi import APIRouter, HTTPException
from backend.app.db.supabase import supabase

router = APIRouter()

# ----------------------------
# GET INVOICES
# ----------------------------
@router.get("/invoices")
def get_invoices():
    try:
        response = supabase.table("invoices").select("*").execute()

        return {
            "data": response.data or []  # ✅ FIX
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# DELETE INVOICE
# ----------------------------
@router.delete("/invoice/{id}")
def delete_invoice(id: str):
    try:
        response = supabase.table("invoices").delete().eq("id", id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Invoice not found")

        return {"status": "success", "deleted_id": id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))