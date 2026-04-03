from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import shutil
import os
import uuid

from backend.app.services.invoice_service import process_invoice

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


# ----------------------------
# HELPER FUNCTION
# ----------------------------
def save_file(file: UploadFile):
    #  Ensure filename is never None
    original_name = file.filename or f"file_{uuid.uuid4().hex}.pdf"

    #  Now safe to use
    ext = os.path.splitext(original_name)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {ext}")

    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path, unique_name

# ----------------------------
# SINGLE FILE UPLOAD ✅ (BEST FOR SWAGGER)
# ----------------------------
@router.post("/upload-single", tags=["Upload"])
async def upload_single(file: UploadFile = File(...)):
    try:
        file_path, filename = save_file(file)

        result = process_invoice(file_path)

        return {
            "status": "success",
            "file": filename,
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# MULTIPLE FILE UPLOAD 🔥
# ----------------------------
@router.post("/upload", tags=["Upload"])
async def upload_multiple(files: List[UploadFile] = File(...)):
    results = []

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    for file in files:
        try:
            file_path, filename = save_file(file)

            result = process_invoice(file_path)

            results.append({
                "file": filename,
                "status": "success",
                "data": result
            })

        except Exception as e:
            results.append({
                "file": file.filename,
                "status": "error",
                "message": str(e)
            })

    return {
        "status": "completed",
        "total_files": len(files),
        "results": results
    }