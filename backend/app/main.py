from fastapi import FastAPI
from backend.app.routes import upload, invoice, analytics
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Invoice AI API", version="1.0.0")

# ----------------------------
# CORS
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# ROUTERS (ALL UNDER /api)
# ----------------------------
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(invoice.router, prefix="/api", tags=["Invoice"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])

# ----------------------------
# ROOT
# ----------------------------
@app.get("/")
def root():
    return {"message": "🚀 Invoice AI Backend Running"}

# ----------------------------
# HEALTH
# ----------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}