import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, DateTime, text


class Tenant(SQLModel, table=True):
    __tablename__ = "tenants"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    name: str
    tier: str = Field(default="pro", sa_column_kwargs={"server_default": "pro"})
    cache_epoch: int = Field(default=1, sa_column_kwargs={"server_default": "1"})
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=text("now()")
        ),
    )
