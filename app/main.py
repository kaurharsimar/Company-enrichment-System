from fastapi import FastAPI
from app.routers import upload, jobs, export
from app.utils.logger import setup_logging

setup_logging()

app = FastAPI(title="Company Enrichment System", version="1.0.0")

app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(jobs.router, prefix="/api", tags=["Jobs"])
app.include_router(export.router, prefix="/api", tags=["Export"])

@app.get("/")
async def root():
    return {"message": "Company Enrichment System API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}