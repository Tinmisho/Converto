from celery import Celery
import os

from config import settings

celery_app = Celery(
    "converto",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600,  # results kept for 1 hour
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, name="convert")
def convert_task(self, job_id: str, input_path: str, source_ext: str, target_ext: str, resize_opts: dict | None):
    from converters.image import convert_image
    from converters.document import convert_document
    from formats import get_group

    output_dir = os.path.join(settings.upload_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{job_id}.{target_ext}")

    group = get_group(source_ext)

    try:
        if group == "image":
            convert_image(input_path, output_path, target_ext, resize_opts)
        elif group == "document":
            convert_document(input_path, output_path, source_ext, target_ext)
        else:
            raise ValueError(f"Unknown format group: {group}")
    except Exception as exc:
        # Clean up failed input
        if os.path.exists(input_path):
            os.remove(input_path)
        raise exc

    # Clean up input after success
    if os.path.exists(input_path):
        os.remove(input_path)

    return {"output_path": output_path}
