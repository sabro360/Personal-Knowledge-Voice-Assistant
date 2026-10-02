"""add_embedding_to_knowledge

Revision ID: 8142d5573c43
Revises: f1e2d3c4b5a6
Create Date: 2026-10-02 15:35:27.211411

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '8142d5573c43'
down_revision: Union[str, Sequence[str], None] = 'f1e2d3c4b5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        from pgvector.sqlalchemy import Vector
        op.add_column("knowledge", sa.Column("embedding", Vector(1536), nullable=True))
    else:
        # SQLite: store as text for schema compatibility (not used for vector search)
        op.add_column("knowledge", sa.Column("embedding", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("knowledge", "embedding")
