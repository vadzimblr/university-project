from infrastructure.celery.app import celery_app
from core.di.container import Container


@celery_app.task(name="scene_segmentation_task", bind=True)
def scene_segmentation_task(
    self,
    job_id: str,
    pdf_bytes: bytes,
    start_page: int = 1,
    end_page: int = 999
):
    container = Container()
    use_case = container.scene_segmentation_use_case()

    try:
        result = use_case.execute(job_id, pdf_bytes, start_page, end_page)
        return {
            "status": "success",
            "scenes_count": result.scenes_count,
            "text_length": result.text_length,
            "message": f"Found {result.scenes_count} scenes in text"
        }
    except Exception as exc:
        raise self.retry(
            exc=exc,
            countdown=60 * (2 ** self.request.retries),
            max_retries=3
        )
