import asyncio
import json
import gc
from app.services.website_detector import detect_website
from app.services.contact_discovery import discover_contacts

from app.utils.logger import logger
from app.jobs.state import jobs, lock, BATCH_SIZE, semaphore

async def run_processing(job_id: str):
    try:
        async with lock:
            jobs[job_id]["status"] = "PROCESSING"

        companies = jobs[job_id]["companies"]
        queue = asyncio.Queue()

        # Producer: Add companies to queue
        async def producer():
            for company in companies:
                await queue.put(company)
            await queue.put(None)  # Sentinel to stop consumers

        # Consumers: Process batches
        async def consumer():
            while True:
                batch = []
                for _ in range(BATCH_SIZE):
                    item = await queue.get()
                    if item is None:
                        queue.task_done()
                        return
                    batch.append(item)
                    queue.task_done()

                async with semaphore:  # Limit concurrent batches
                    await process_batch(job_id, batch)

        # Start producer and multiple consumers
        producer_task = asyncio.create_task(producer())
        consumer_tasks = [asyncio.create_task(consumer()) for _ in range(MAX_CONCURRENT_BATCHES)]

        await producer_task
        await asyncio.gather(*consumer_tasks)

        async with lock:
            jobs[job_id]["status"] = "COMPLETED"
            # Final save to temp file
            with open(jobs[job_id]["temp_file"], "w") as f:
                json.dump(jobs[job_id]["results"], f)

    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        async with lock:
            jobs[job_id]["status"] = "FAILED"


async def process_batch(job_id: str, batch: List[str]):
    tasks = [process_company(job_id, company) for company in batch]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    async with lock:
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Batch processing error: {str(result)}")
                jobs[job_id]["failure_count"] += 1
            else:
                jobs[job_id]["results"].append(result)
                jobs[job_id]["success_count"] += 1
        jobs[job_id]["processed"] += len(batch)

        # Incremental save every 1000 results to manage memory
        if len(jobs[job_id]["results"]) % 1000 == 0:
            with open(jobs[job_id]["temp_file"], "w") as f:
                json.dump(jobs[job_id]["results"], f)
            gc.collect()  # Hint for garbage collection


async def process_company(job_id: str, company: str):
    try:
        website_info = await detect_website(company)
        result = {
            "company": company,
            "website": website_info["website_url"],
            "website_found": website_info["website_found"],
            "phone": None,
            "phone_found": False,
            "email": None,
            "email_found": False,
            "source": "Website Detection",
            "status": "success"
        }

        if not website_info["website_found"]:
            contact_info = await discover_contacts(company)
            result.update(contact_info)
            result["source"] = contact_info["source"]

        return result
    except Exception as e:
        logger.error(f"Failed to process {company}: {str(e)}")
        return {
            "company": company,
            "website": None,
            "website_found": False,
            "phone": None,
            "phone_found": False,
            "email": None,
            "email_found": False,
            "source": None,
            "status": "failed"
        }