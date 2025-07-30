from io import BytesIO
from PyPDF2 import PdfReader

class PdfTextExtractorService:
    def __init__(self, pdf_bytes: bytes):
        self.reader = PdfReader(BytesIO(pdf_bytes))
        self.total_pages = len(self.reader.pages)

    def extract_text(self, start_page: int, end_page: int) -> str:
        start_page = max(1, start_page)
        end_page = min(end_page, self.total_pages)

        if start_page > end_page:
            raise ValueError("start_page cannot be greater than end_page")

        result = []
        for i in range(start_page - 1, end_page):
            text = self.reader.pages[i].extract_text()
            if text:
                result.append(text.strip())

        return "\n\n".join(result)
