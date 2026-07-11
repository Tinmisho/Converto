from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from tasks.celery_app import celery_app

router = APIRouter()


@router.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    result = AsyncResult(job_id, app=celery_app)

    state = result.state  # PENDING, STARTED, SUCCESS, FAILURE

    if state == "FAILURE":
        return {
            "job_id": job_id,
            "status": "failed",
            "error": str(result.result),
        }

    if state == "SUCCESS":
        return {
            "job_id": job_id,
            "status": "done",
            "download_url": f"/api/download/{job_id}",
        }

    return {
        "job_id": job_id,
        "status": "pending" if state == "PENDING" else "converting",
    }
