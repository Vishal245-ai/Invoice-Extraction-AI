🚀 Invoice AI – Enterprise Invoice Processing System

AI-powered full-stack application for extracting, processing, and analyzing invoice data using OCR and LLMs.

🔗 Live Demo
🌐 Frontend: https://your-frontend.vercel.app
⚙️ Backend API: https://your-backend.onrender.com/docs
📌 Overview

Invoice AI automates invoice data extraction using a hybrid pipeline:

📄 OCR for text extraction
🧠 Rule-based + AI (Gemini) parsing
🧾 Structured data normalization
🔁 Duplicate detection system
📊 Real-time analytics dashboard

-- System Architecture
Frontend (React + Vite)
        ↓
REST API (/api)
        ↓
FastAPI Backend
        ↓
OCR Engine (Tesseract + pdf2image)
        ↓
Smart Parser (Regex + Table Extraction)
        ↓
LLM Cleanup (Gemini API)
        ↓
Supabase (PostgreSQL)


✨ Features
- Invoice Processing
Upload multiple invoices (PDF/Image)
Drag & drop support
Automatic OCR extraction

🧠 Intelligent Parsing
Multi-line product extraction
Multi-brand support (OnePlus, Amazon, Flipkart, etc.)
Vendor normalization
Price + tax extraction

🔁 Duplicate Handling
Detect duplicates using:
vendor_name
invoice_number
total
Stores duplicates with flag (is_duplicate)

📊 Dashboard
Vendor-wise spend
Invoice tracking
Data visualization using charts
🗑️ Invoice Management
View all invoices
Delete invoices
Safe rendering (handles missing data)

 -- Tech Stack

🔹 Frontend
React (Vite)
Recharts
🔹 Backend
FastAPI
Supabase (PostgreSQL)
🔹 AI & Processing
OCR: Tesseract + pdf2image
LLM: Gemini API
Regex + rule-based parsing


📁 Project Structure
backend/
  app/
    routes/
    services/
    utils/
    db/
    schemas/

frontend/
  src/
    pages/
    services/

sample_data/
docs/
⚙️ Installation
🔹 Backend
cd backend
pip install -r requirements.txt
uvicorn backend.app.main:app --reload

🔹 Frontend
cd frontend
npm install
npm run dev

🔑 Environment Variables
Backend (.env)
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
GEMINI_API_KEY=your_key
Frontend (.env)
VITE_API_URL=http://localhost:8000/api

🎯 Key Design Decisions
Hybrid approach (Regex + LLM) for accuracy
Table-based parsing for robustness
Vendor normalization for consistency
Duplicate detection using composite keys
Modular service architecture

⚠️ Assumptions & Limitations
OCR accuracy depends on invoice quality
LLM output may vary slightly
PDF parsing requires system dependencies:
poppler
tesseract
Single-product optimization (multi-product support optional)

🚀 Potential Improvements
Multi-product invoice support
Cloud OCR (AWS Textract / Google Vision)
Authentication (Supabase Auth)
Pagination & filtering
Async processing (Celery / queues)
Product categorization (AI-based)

📊 API Endpoints
Method	Endpoint	Description
POST	/api/upload	Upload invoices
GET	/api/invoices	Get all invoices
DELETE	/api/invoice/{id}	Delete invoice
