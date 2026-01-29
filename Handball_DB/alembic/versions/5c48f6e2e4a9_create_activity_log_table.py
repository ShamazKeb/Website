"""create activity_log table

Revision ID: 5c48f6e2e4a9
Revises: 11e9b76f0dec
Create Date: 2026-01-29 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.models import ActionType


# revision identifiers, used by Alembic.
revision: str = '5c48f6e2e4a9'
down_revision: Union[str, Sequence[str], None] = '11e9b76f0dec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.Enum(ActionType), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('target_player_id', sa.Integer(), nullable=True),
        sa.Column('target_exercise_id', sa.Integer(), nullable=True),
        sa.Column('target_team_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['target_exercise_id'], ['exercises.id'], ),
        sa.ForeignKeyConstraint(['target_player_id'], ['players.id'], ),
        sa.ForeignKeyConstraint(['target_team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activity_logs_id'), 'activity_logs', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_activity_logs_id'), table_name='activity_logs')
    op.drop_table('activity_logs')
