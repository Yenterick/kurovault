import uuid
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.documents_repository import DocumentsRepository
from app.services.documents_service import DocumentsService
from app.core.pg_connection import get_db

router = APIRouter()


@router.post("/upload")
async def upload_document(
    request: Request,
    tenant_id: uuid.UUID = Form(...),
    priority: str = Form("high_priority"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    repo = DocumentsRepository(db)
    service = DocumentsService(repo, request.app.state.arq_pool)

    doc, is_duplicate = await service.ingest_upload(tenant_id, file, priority)
    await db.commit()

    status_code = status.HTTP_200_OK if is_duplicate else status.HTTP_202_ACCEPTED
    return JSONResponse(
        status_code=status_code,
        content={
            "document_id": str(doc.id),
            "status": doc.status,
            "duplicate": is_duplicate,
        },
    )
