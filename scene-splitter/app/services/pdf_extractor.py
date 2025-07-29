from io import BytesIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_bytes: bytes, start_page: int, end_page: int) -> str:
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        total_pages = len(reader.pages)

        start_page = max(1, start_page)
        end_page = min(end_page, total_pages)

        if start_page > end_page:
            raise ValueError("start_page cannnot be more then end_page")

        extracted_text = []
        for i in range(start_page - 1, end_page):
            text = reader.pages[i].extract_text()
            if text:
                extracted_text.append(text.strip())

        return "\n\n".join(extracted_text)
    except Exception as e:
        raise ValueError("Error while extracting text from PDF") from e
