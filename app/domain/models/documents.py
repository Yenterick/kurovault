import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlmodel import SQLModel, Field, Column, DateTime, UniqueConstraint, CHAR, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB


class Status(str, Enum):
    pending = "PENDING"
    processing = "PROCESSING"
    completed = "COMPLETED"
    failed = "FAILED"


class Document(SQLModel, table=True):
    __tablename__ = "documents"
    __table_args__ = (UniqueConstraint("tenant_id", "file_hash"),)

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    tenant_id: uuid.UUID = Field(
        foreign_key="tenants.id", ondelete="CASCADE", nullable=False
    )
    filename: str
    file_hash: str = Field(sa_column=Column(CHAR(64), nullable=False))
    status: Status = Field(
        default=Status.pending,
        sa_column=Column(
            SAEnum(
                Status,
                native_enum=False,
                length=None,
                values_callable=lambda e: [m.value for m in e],
            ),
            nullable=False,
            server_default=Status.pending.value,
        ),
    )
    error_message: str | None = Field(default=None)
    doc_metadata: dict = Field(
        default_factory=dict,
        sa_column=Column(
            "metadata", JSONB, nullable=False, server_default=text("'{}'::jsonb")
        ),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=text("now()")
        ),
    )
