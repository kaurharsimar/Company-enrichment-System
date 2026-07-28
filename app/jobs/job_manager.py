import asyncio
import uuid
import json
import os
from typing import Dict, List

from app.utils.logger import logger
from app.jobs.state import jobs, lock, BATCH_SIZE, semaphore
from app.jobs.background_tasks import run_processing

jobs: Dict[str, Dict] = {}  # In-memory; use Redis/DB in production
lock = asyncio.Lock()
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 50))
MAX_CONCURRENT_BATCHES = int(os.getenv("MAX_CONCURRENT_BATCHES", 5))
semaphore = asyncio.Semaphore(MAX_CONCURRENT_BATCHES)

async def create_job(companies: List[str]) -> str:
    job_id = str(uuid.uuid4())
    async with lock:
        jobs[job_id] = {
            "status": "PENDING",
            "total": len(companies),
            "processed": 0,
            "success_count": 0,
            "failure_count": 0,
            "results": [],
            "companies": companies,
            "temp_file": f"/tmp/{job_id}_results.json"  # For incremental saving
        }
    return job_id

async def start_background_processing(job_id: str, background_tasks):
    background_tasks.add_task(run_processing, job_id)

def get_job_status(job_id: str) -> Dict:
    return jobs.get(job_id)

def get_job_results(job_id: str) -> List[Dict]:
    job = jobs.get(job_id)
    if not job:
        return []
    # Load from temp file if exists
    if os.path.exists(job["temp_file"]):
        with open(job["temp_file"], "r") as f:
            return json.load(f)
    return job["results"]