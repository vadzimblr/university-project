from app.utils.celery import celery_app
from app.services.pdf_extractor import PdfTextExtractorService
from app.services.scene_splitter import split_into_scenes

@celery_app.task(name="extract_text_task")
def extract_text_task(pdf_bytes: bytes, start_page: int, end_page: int):
    service = PdfTextExtractorService(pdf_bytes)
    text = service.extract_text(start_page, end_page)

    return split_into_scenes(text)
