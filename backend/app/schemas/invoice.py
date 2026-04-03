from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


# ----------------------------
# Line Item Schema
# ----------------------------
class LineItem(BaseModel):
    # Existing flexible fields
    description: Optional[str] = None
    
    # New structured fields (from your update)
    product_name: Optional[str] = None
    
    quantity: Optional[float] = None
    
    # Mapping both styles
    unit_price: Optional[float] = None
    price: Optional[float] = None
    
    amount: Optional[float] = None


# ----------------------------
# Invoice Base Schema
# ----------------------------
class InvoiceBase(BaseModel):
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None   # keep string for simplicity
    due_date: Optional[str] = None
    currency: Optional[str] = None

    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None

    # Updated line items (default empty list)
    line_items: List[LineItem] = []

    # Confidence score (bounded)
    confidence_score: Optional[float] = Field(default=0.0, ge=0, le=1)


# ----------------------------
# Create Schema (input)
# ----------------------------
class InvoiceCreate(InvoiceBase):
    pass


# ----------------------------
# DB Schema (output)
# ----------------------------
class InvoiceDB(InvoiceBase):
    id: Optional[str]
    is_duplicate: Optional[bool] = False
    created_at: Optional[str]

    class Config:
        from_attributes = True


# ----------------------------
# Response Schema
# ----------------------------
class InvoiceResponse(BaseModel):
    status: str
    data: InvoiceDB