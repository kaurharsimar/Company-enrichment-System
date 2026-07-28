from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from app.services.file_processor import process_file
from app.jobs.job_manager import create_job, start_background_processing

router = APIRouter()

@router.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if file.filename.endswith(('.xlsx', '.csv')):
        try:
            companies = await process_file(file)
            job_id = create_job(companies)
            start_background_processing(job_id, background_tasks)
            return {"job_id": job_id, "message": "Processing started"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Only .xlsx and .csv files are supported")