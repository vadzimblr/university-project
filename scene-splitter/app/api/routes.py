from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.tasks.extract_text_task import extract_text_task

router = APIRouter()

@router.post("/split-scenes/")
async def split_scenes_from_pdf(
    file: UploadFile = File(...),
    start_page: int = Form(1),
    end_page: int = Form(999)
):
    pdf_bytes = await file.read()
    task = extract_text_task.delay(pdf_bytes, start_page, end_page)

    return {"task_id": task.id}
