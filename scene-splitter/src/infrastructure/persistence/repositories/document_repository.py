from sqlalchemy.orm import Session
from typing import Optional

from domain.entities.document import Document


class DocumentRepository:
    def __init__(
            self,
            db_session: Session
    ):
        self.db_session = db_session

    def create(
            self,
            filename: str,
            file_size: Optional[int] = None,
            mime_type: Optional[str] = None,
            commit: bool = True
    ) -> Document:
        document = Document(
            filename=filename,
            file_size=file_size,
            mime_type=mime_type
        )
        self.db_session.add(document)

        if commit:
            self.db_session.commit()
            self.db_session.refresh(document)
        else:
            self.db_session.flush()

        return document

    def get_by_id(self, document_id: str) -> Optional[Document]:
        return self.db_session.query(Document).filter(Document.id == document_id).first()

    def update(self, document: Document, commit: bool = True) -> Document:
        if commit:
            self.db_session.commit()
            self.db_session.refresh(document)
        return document

    def delete(self, document_id: str) -> bool:
        document = self.get_by_id(document_id)

        if document:
            self.db_session.delete(document)
            self.db_session.commit()
            return True

        return False
