from io import BytesIO
from typing import List

from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams


class PdfTextExtractorService:

    def __init__(self, pdf_bytes: bytes):
        self.pdf_bytes = pdf_bytes
        self.reader = PdfReader(BytesIO(pdf_bytes))
        self.total_pages = len(self.reader.pages)

    def extract_text(self, start_page: int, end_page: int) -> str:
        start_page = max(1, start_page)
        end_page = min(end_page, self.total_pages)

        if start_page > end_page:
            raise ValueError("start_page cannot be greater than end_page")

        page_numbers: List[int] = list(range(start_page - 1, end_page))

        laparams = LAParams(
            char_margin=2.0,
            word_margin=0.1,
            line_margin=0.5,
            boxes_flow=None,
        )

        text = extract_text(BytesIO(self.pdf_bytes), page_numbers=page_numbers, laparams=laparams)
        return text.strip()
