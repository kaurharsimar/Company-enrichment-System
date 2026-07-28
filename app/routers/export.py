from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.jobs.job_manager import get_job_results
import pandas as pd
import os

router = APIRouter()


@router.get("/export/{job_id}/with-website")
async def export_with_website(job_id: str):
    results = get_job_results(job_id)
    if not results:
        raise HTTPException(status_code=404, detail="Job not found or not completed")

    with_website = [r for r in results if r["website_found"]]
    df = pd.DataFrame(with_website)
    file_path = f"/tmp/{job_id}_with_website.csv"
    df.to_csv(file_path, index=False)
    return FileResponse(file_path, media_type='text/csv', filename='companies_with_website.csv')


@router.get("/export/{job_id}/without-website")
async def export_without_website(job_id: str):
    results = get_job_results(job_id)
    if not results:
        raise HTTPException(status_code=404, detail="Job not found or not completed")

    without_website = [r for r in results if not r["website_found"]]
    df = pd.DataFrame(without_website)
    file_path = f"/tmp/{job_id}_without_website.csv"
    df.to_csv(file_path, index=False)
    return FileResponse(file_path, media_type='text/csv', filename='companies_without_website.csv')