import uuid
from sqlmodel import SQLModel, Field, Column, text
from sqlalchemy.dialects.postgresql import JSONB


class ParentChunk(SQLModel, table=True):
    __tablename__ = "parent_chunks"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    document_id: uuid.UUID = Field(
        foreign_key="documents.id", ondelete="CASCADE", nullable=False
    )
    tenant_id: uuid.UUID = Field(
        foreign_key="tenants.id", ondelete="CASCADE", nullable=False
    )
    chunk_index: int
    content: str
    chunk_metadata: dict = Field(
        default_factory=dict,
        sa_column=Column(
            "metadata", JSONB, nullable=False, server_default=text("'{}'::jsonb")
        ),
    )
