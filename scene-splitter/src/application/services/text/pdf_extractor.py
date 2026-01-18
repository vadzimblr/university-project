from PyPDF2 import PdfReader
from io import BytesIO

from application.services.text.abstract_text_extractor import AbstractFileTextExtractor
from domain.exceptions.processing_jobs.invalid_page_number_exception import InvalidPageNumberException


class PdfExtractor(AbstractFileTextExtractor):
    def extract(self, file: bytes, start_page: int|None, end_page: int|None) -> str:
        reader = PdfReader(BytesIO(file))
        total_pages = len(reader.pages)
        start_page = max(1, start_page)
        end_page = min(end_page, total_pages)

        if start_page > end_page:
            raise InvalidPageNumberException("start_page cannot be greater than end_page")

        result = []
        for i in range(start_page - 1, end_page):
            text = reader.pages[i].extract_text()
            if text:
                result.append(text.strip())

        return "".join(result)
