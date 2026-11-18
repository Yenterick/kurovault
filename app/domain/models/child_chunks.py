import uuid
from sqlmodel import SQLModel, Field, Column, Index, text
from sqlalchemy import Computed
from sqlalchemy.dialects.postgresql import TSVECTOR
from pgvector.sqlalchemy import HALFVEC

EMBEDDING_DIM = 1536


class ChildChunk(SQLModel, table=True):
    __tablename__ = "child_chunks"
    __table_args__ = (
        Index("idx_child_chunks_tenant", "tenant_id"),
        Index("idx_child_chunks_fts", "fts_tokens", postgresql_using="gin"),
        Index(
            "idx_child_chunks_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "halfvec_cosine_ops"},
        ),
    )

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    parent_id: uuid.UUID = Field(
        foreign_key="parent_chunks.id", ondelete="CASCADE", nullable=False
    )
    document_id: uuid.UUID = Field(
        foreign_key="documents.id", ondelete="CASCADE", nullable=False
    )
    tenant_id: uuid.UUID = Field(
        foreign_key="tenants.id", ondelete="CASCADE", nullable=False
    )
    content: str
    embedding: list[float] = Field(
        sa_column=Column(HALFVEC(EMBEDDING_DIM), nullable=False)
    )
    fts_tokens: str | None = Field(
        default=None,
        sa_column=Column(
            TSVECTOR,
            Computed("to_tsvector('english', content)", persisted=True),
        ),
    )
