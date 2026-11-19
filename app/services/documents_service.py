import hashlib
import uuid
from pathlib import Path

from pathlib import Path

from arq.connections import ArqRedis
from fastapi import UploadFile

from app.domain.models.documents import Document
from app.repositories.documents_repository import DocumentsRepository

UPLOAD_DIR = Path("./uploads")


class DocumentsService:
    def __init__(
        self,
        documents_repository: DocumentsRepository,
        arq_pool: ArqRedis,
    ) -> None:
        self.repository = documents_repository
        self.arq_pool = arq_pool

    async def get_by_hash(
        self, tenant_id: uuid.UUID, file_hash: str
    ) -> Document | None:
        return await self.repository.get_by_hash(tenant_id, file_hash)

    async def ingest_upload(
        self,
        tenant_id: uuid.UUID,
        file: UploadFile,
        priority: str = "high_priority",
    ) -> tuple[Document, bool]:
        tenant_dir = UPLOAD_DIR / str(tenant_id)
        tenant_dir.mkdir(parents=True, exist_ok=True)
        temp_path = tenant_dir / f"{uuid.uuid4()}_{file.filename}"

        hasher = hashlib.sha256()
        file_size = 0
        with temp_path.open("wb") as buffer:
            while chunk := await file.read(65_536):
                hasher.update(chunk)
                buffer.write(chunk)
                file_size += len(chunk)

        file_hash = hasher.hexdigest()

        existing_doc = await self.repository.get_by_hash(tenant_id, file_hash)
        if existing_doc is not None:
            temp_path.unlink(missing_ok=True)
            return existing_doc, True

        new_doc = await self.repository.create_pending_and_bump_epoch(
            tenant_id=tenant_id,
            filename=file.filename or "untitled",
            file_hash=file_hash,
            metadata={
                "storage_path": str(temp_path),
                "content_type": file.content_type,
                "size_bytes": file_size,
            },
        )

        await self.arq_pool.enqueue_job(
            "process_document_task",
            str(new_doc.id),
            str(tenant_id),
            _queue_name=priority,
        )

        return new_doc, False
