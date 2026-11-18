import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, DateTime, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PG_UUID


class QueryTrace(SQLModel, table=True):
    __tablename__ = "query_traces"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    tenant_id: uuid.UUID = Field(
        foreign_key="tenants.id", ondelete="CASCADE", nullable=False
    )
    user_query: str
    cache_hit: bool = Field(
        default=False, sa_column_kwargs={"server_default": text("false")}
    )
    ttft_ms: int | None = Field(default=None)
    total_latency_ms: int | None = Field(default=None)
    agent_steps: list[dict] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default=text("'[]'::jsonb")),
    )
    cited_chunk_ids: list[uuid.UUID] = Field(
        default_factory=list,
        sa_column=Column(
            ARRAY(PG_UUID(as_uuid=True)),
            nullable=False,
            server_default=text("'{}'::uuid[]"),
        ),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=text("now()")
        ),
    )
