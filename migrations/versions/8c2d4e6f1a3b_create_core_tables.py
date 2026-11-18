"""create core tables

Revision ID: 8c2d4e6f1a3b
Revises: 3f681fb49383
Create Date: 2026-11-17 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy
from sqlalchemy.dialects import postgresql

revision: str = "8c2d4e6f1a3b"
down_revision: Union[str, Sequence[str], None] = "3f681fb49383"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column(
            "id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("tier", sa.String(), server_default="pro", nullable=False),
        sa.Column("cache_epoch", sa.Integer(), server_default="1", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "documents",
        sa.Column(
            "id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("file_hash", sa.CHAR(64), nullable=False),
        sa.Column("status", sa.String(), server_default="PENDING", nullable=False),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "file_hash"),
    )

    op.create_table(
        "parent_chunks",
        sa.Column(
            "id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "child_chunks",
        sa.Column(
            "id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("parent_id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("embedding", pgvector.sqlalchemy.HALFVEC(1536), nullable=False),
        sa.Column(
            "fts_tokens",
            postgresql.TSVECTOR(),
            sa.Computed("to_tsvector('english', content)", persisted=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["parent_chunks.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_child_chunks_tenant", "child_chunks", ["tenant_id"])
    op.create_index(
        "idx_child_chunks_fts", "child_chunks", ["fts_tokens"], postgresql_using="gin"
    )
    op.create_index(
        "idx_child_chunks_hnsw",
        "child_chunks",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_with={"m": 16, "ef_construction": 64},
        postgresql_ops={"embedding": "halfvec_cosine_ops"},
    )

    op.create_table(
        "query_traces",
        sa.Column(
            "id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("user_query", sa.String(), nullable=False),
        sa.Column(
            "cache_hit", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("ttft_ms", sa.Integer(), nullable=True),
        sa.Column("total_latency_ms", sa.Integer(), nullable=True),
        sa.Column(
            "agent_steps",
            postgresql.JSONB(),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "cited_chunk_ids",
            postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
            server_default=sa.text("'{}'::uuid[]"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("query_traces")
    op.drop_index("idx_child_chunks_hnsw", table_name="child_chunks")
    op.drop_index("idx_child_chunks_fts", table_name="child_chunks")
    op.drop_index("idx_child_chunks_tenant", table_name="child_chunks")
    op.drop_table("child_chunks")
    op.drop_table("parent_chunks")
    op.drop_table("documents")
    op.drop_table("tenants")
