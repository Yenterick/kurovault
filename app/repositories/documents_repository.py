import uuid
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models import Document, Tenant


class DocumentsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_hash(
        self, tenant_id: uuid.UUID, file_hash: str
    ) -> Document | None:
        stmt = select(Document).where(
            Document.tenant_id == tenant_id,
            Document.file_hash == file_hash,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_pending_and_bump_epoch(
        self, tenant_id: uuid.UUID, filename: str, file_hash: str, metadata: dict
    ) -> Document:
        doc = Document(
            tenant_id=tenant_id,
            filename=filename,
            file_hash=file_hash,
            status="PENDING",
            doc_metadata=metadata,
        )
        self.session.add(doc)

        await self.session.execute(
            update(Tenant)
            .where(Tenant.id == tenant_id)
            .values(cache_epoch=Tenant.cache_epoch + 1)
        )
        await self.session.flush()
        return doc
