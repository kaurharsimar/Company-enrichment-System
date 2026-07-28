from fastapi import APIRouter, HTTPException
from app.jobs.job_manager import get_job_status

router = APIRouter()

@router.get("/job/{job_id}")
async def get_job(job_id: str):
    status = get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return status