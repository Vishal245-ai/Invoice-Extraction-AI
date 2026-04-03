-- Enable UUID
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =========================
-- USERS
-- =========================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- INVOICES
-- =========================
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    file_name TEXT,
    file_url TEXT,

    vendor_name TEXT,
    invoice_number TEXT,
    invoice_date TEXT,
    due_date TEXT,

    currency TEXT DEFAULT 'INR',
    subtotal FLOAT,
    tax FLOAT,
    total FLOAT,

    confidence_score FLOAT DEFAULT 0.7,
    highlights JSONB,

    is_duplicate BOOLEAN DEFAULT FALSE,

    raw_text TEXT,
    parsed_data JSONB,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vendor_name ON invoices(vendor_name);
CREATE INDEX IF NOT EXISTS idx_invoice_number ON invoices(invoice_number);

-- =========================
-- LINE ITEMS
-- =========================
CREATE TABLE IF NOT EXISTS invoice_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,

    description TEXT,
    quantity FLOAT,
    unit_price FLOAT,
    amount FLOAT
);

-- =========================
-- FORMAT LEARNING 🔥
-- =========================
CREATE TABLE IF NOT EXISTS invoice_formats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_name TEXT,
    sample_structure JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_format_vendor ON invoice_formats(vendor_name);