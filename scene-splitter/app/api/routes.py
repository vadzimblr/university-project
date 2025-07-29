from fastapi import File, UploadFile, APIRouter, Form
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.scene_splitter import split_into_scenes
from app.services.pdf_cleaner import clean_pdf_text

router = APIRouter()

@router.post("/split-scenes/")
async def split_scenes_from_pdf(
    file: UploadFile = File(...),
    start_page: int = Form(1),
    end_page: int = Form(999)
):
    pdf_bytes = await file.read()

    try:
        text = extract_text_from_pdf(pdf_bytes, start_page, end_page)
        text = clean_pdf_text(text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    scenes = split_into_scenes(text)
    return {"scenes": scenes}
