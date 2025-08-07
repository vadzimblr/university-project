from app.utils.celery import celery_app
from app.services.pdf_extractor import PdfTextExtractorService
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.utils.database import get_db_session
from app.services.tasks.scene_splitting_task import scene_splitting_task
from sqlalchemy.orm import Session


@celery_app.task(name="extract_text_task", bind=True)
def extract_text_task(self, job_id: str, pdf_bytes: bytes, start_page: int = 1, end_page: int = 999):
    session: Session = get_db_session()
    job_repo = ProcessingJobRepository(session)
    
    try:
        job_repo.update_status(job_id, "extracting", "text_extraction")
        
        service = PdfTextExtractorService(pdf_bytes)
        extracted_text = service.extract_text(start_page, end_page)
        
        if not extracted_text.strip():
            raise ValueError("No text extracted from PDF file")
        
        scene_splitting_task.delay(job_id, extracted_text)
        
        return {
            'status': 'success',
            'text_length': len(extracted_text),
            'message': f'Extracted text with {len(extracted_text)} characters'
        }
        
    except Exception as e:
        job_repo.update_status(job_id, "failed", error_message=str(e))
        
        raise self.retry(
            exc=e,
            countdown=60 * (2 ** self.request.retries),
            max_retries=3
        )
    
    finally:
        session.close()
