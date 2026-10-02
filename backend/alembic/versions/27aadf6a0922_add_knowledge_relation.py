"""add_knowledge_relation

Revision ID: 27aadf6a0922
Revises: 8142d5573c43
Create Date: 2026-10-02 16:01:01.791873

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '27aadf6a0922'
down_revision: Union[str, Sequence[str], None] = '8142d5573c43'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the knowledge_relations table."""
    op.create_table(
        'knowledge_relations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source_knowledge_id', sa.Integer(), nullable=False),
        sa.Column('target_knowledge_id', sa.Integer(), nullable=False),
        sa.Column('relation_type', sa.String(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['source_knowledge_id'], ['knowledge.id']),
        sa.ForeignKeyConstraint(['target_knowledge_id'], ['knowledge.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'source_knowledge_id', 'target_knowledge_id', name='uq_knowledge_relation'
        ),
    )


def downgrade() -> None:
    """Drop the knowledge_relations table."""
    op.drop_table('knowledge_relations')
