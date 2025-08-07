from typing import Optional, List
from sqlalchemy.orm import Session

from ..models.document import Document


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, filename: str, file_size: Optional[int] = None, mime_type: Optional[str] = None) -> Document:
        document = Document(
            filename=filename,
            file_size=file_size,
            mime_type=mime_type
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def get_by_id(self, document_id: str) -> Optional[Document]:
        return self.db.query(Document).filter(Document.id == document_id).first()
    
    def get_by_filename(self, filename: str) -> Optional[Document]:
        return self.db.query(Document).filter(Document.filename == filename).first()
    
    def update(self, document: Document) -> Document:
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def delete(self, document_id: str) -> bool:
        document = self.get_by_id(document_id)
        if document:
            self.db.delete(document)
            self.db.commit()
            return True
        return False 