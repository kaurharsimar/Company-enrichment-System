# Company Enrichment System

A FastAPI backend to process company names from Excel/CSV files, detect websites, and find contacts using official APIs.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables in `.env` (copy from `.env.example`).
3. Run: `uvicorn app.main:app --reload`

## Endpoints
- POST /api/upload: Upload file and start processing.
- GET /api/job/{job_id}: Check job status.
- GET /api/export/{job_id}/with-website: Download CSV for companies with websites.
- GET /api/export/{job_id}/without-website: Download CSV for companies without websites.

## Notes
- Handles up to 20,000 records with batching and async processing.
- Uses Google Places API (requires API key).
- Email discovery is limited by API; marked as not found.
- For production, add database persistence and monitoring.
