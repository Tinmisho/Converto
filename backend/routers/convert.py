from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
import uuid, os, aiofiles
from config import settings
from formats import is_supported, get_targets, get_group, ALL_FORMATS, CONVERSION_TARGETS
from tasks.celery_app import convert_task

router = APIRouter()


@router.get("/formats")
def list_formats():
    """Return the full format support matrix for the frontend."""
    return {
        "formats": ALL_FORMATS,
        "targets": CONVERSION_TARGETS,
    }


@router.post("/convert")
async def upload_and_convert(
    file: UploadFile = File(...),
    target_format: str = Form(...),
    resize_width: int | None = Form(None),
    resize_height: int | None = Form(None),
    resize_scale: float | None = Form(None),
):
    # Validate file size
    max_bytes = settings.max_file_mb * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(413, f"File too large. Max {settings.max_file_mb} MB.")

    # Validate extension
    ext = os.path.splitext(file.filename or "")[1].lower().lstrip(".")
    if not is_supported(ext):
        raise HTTPException(400, f"Unsupported format: .{ext}")

    targets = get_targets(ext)
    if target_format not in targets:
        raise HTTPException(400, f"Cannot convert .{ext} to .{target_format}")

    # Validate resize params (images only)
    group = get_group(ext)
    resize_opts = None
    if resize_width or resize_height or resize_scale:
        if group != "image":
            raise HTTPException(400, "Resize is only supported for images.")
        if resize_scale and (resize_width or resize_height):
            raise HTTPException(400, "Use either scale or width/height, not both.")
        resize_opts = {
            "width": resize_width,
            "height": resize_height,
            "scale": resize_scale,
        }

    # Save uploaded file
    job_id = str(uuid.uuid4())
    input_dir = os.path.join(settings.upload_dir, "input")
    input_path = os.path.join(input_dir, f"{job_id}.{ext}")

    async with aiofiles.open(input_path, "wb") as f:
        await f.write(content)

    # Queue the task
    convert_task.apply_async(
        args=[job_id, input_path, ext, target_format, resize_opts],
        task_id=job_id,
    )

    return {
        "job_id": job_id,
        "original_name": file.filename,
        "source_format": ext,
        "target_format": target_format,
        "resize": resize_opts,
    }


@router.get("/download/{job_id}")
def download_result(job_id: str, filename: str = "converted"):
    output_dir = os.path.join(settings.upload_dir, "output")
    # Find the output file for this job
    for f in os.listdir(output_dir):
        if f.startswith(job_id):
            ext = os.path.splitext(f)[1]
            return FileResponse(
                os.path.join(output_dir, f),
                filename=f"{filename}{ext}",
                media_type="application/octet-stream",
            )
    raise HTTPException(404, "Output file not found.")
