from contextlib import AbstractContextManager
from typing import Optional, List, Callable
from sqlalchemy.orm import Session

from domain.entities.document import Document


class DocumentRepository:
    def __init__(
            self,
            session_factory: Callable[..., AbstractContextManager[Session]]
    ):
        self.session_factory = session_factory

    def create(self, filename: str, file_size: Optional[int] = None, mime_type: Optional[str] = None) -> Document:
        with self.session_factory() as session:
            document = Document(
                filename=filename,
                file_size=file_size,
                mime_type=mime_type
            )
            self.session.add(document)
            self.session.commit()
            self.session.refresh(document)
            return document

    def get_by_id(self, document_id: str) -> Optional[Document]:
        return self.session.query(Document).filter(Document.id == document_id).first()

    def update(self, document: Document) -> Document:
        self.session.commit()
        self.session.refresh(document)
        return document

    def delete(self, document_id: str) -> bool:
        document = self.get_by_id(document_id)

        if document:
            self.session.delete(document)
            self.session.commit()
            return True

        return False
