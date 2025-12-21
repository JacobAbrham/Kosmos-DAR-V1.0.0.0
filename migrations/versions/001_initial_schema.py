"""Initial schema - users, conversations, votes

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'operator', 'user',
                  'agent', 'readonly', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'),
                    'users', ['username'], unique=True)

    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('key_hash', sa.String(length=64), nullable=False),
        sa.Column('key_prefix', sa.String(length=12), nullable=False),
        sa.Column('scopes', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_keys_user_id'),
                    'api_keys', ['user_id'], unique=False)
    op.create_index(op.f('ix_api_keys_key_hash'),
                    'api_keys', ['key_hash'], unique=True)

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('conversation_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('agent_name', sa.String(length=50), nullable=True),
        sa.Column('model_used', sa.String(length=100), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_conversation_id'),
                    'conversations', ['conversation_id'], unique=True)
    op.create_index(op.f('ix_conversations_user_id'),
                    'conversations', ['user_id'], unique=False)

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('input_tokens', sa.Integer(), nullable=True),
        sa.Column('output_tokens', sa.Integer(), nullable=True),
        sa.Column('model_used', sa.String(length=100), nullable=True),
        sa.Column('agent_name', sa.String(length=50), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], [
                                'conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_conversation_id'),
                    'messages', ['conversation_id'], unique=False)

    # Create proposals table
    op.create_table(
        'proposals',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('proposal_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('cost', sa.Float(), nullable=False, default=0.0),
        sa.Column('status', sa.String(length=20),
                  nullable=False, default='pending'),
        sa.Column('final_score', sa.Float(), nullable=True),
        sa.Column('threshold_used', sa.Float(), nullable=True),
        sa.Column('initiated_by_agent', sa.String(length=50), nullable=True),
        sa.Column('initiated_by_user_id', sa.Integer(), nullable=True),
        sa.Column('context', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['initiated_by_user_id'], [
                                'users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_proposals_proposal_id'),
                    'proposals', ['proposal_id'], unique=True)
    op.create_index(op.f('ix_proposals_status'),
                    'proposals', ['status'], unique=False)

    # Create votes table
    op.create_table(
        'votes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('proposal_id', sa.Integer(), nullable=False),
        sa.Column('agent_name', sa.String(length=50), nullable=False),
        sa.Column('vote', sa.String(length=10), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False, default=1.0),
        sa.Column('reasoning', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['proposal_id'], ['proposals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_votes_proposal_id'), 'votes',
                    ['proposal_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_votes_proposal_id'), table_name='votes')
    op.drop_table('votes')

    op.drop_index(op.f('ix_proposals_status'), table_name='proposals')
    op.drop_index(op.f('ix_proposals_proposal_id'), table_name='proposals')
    op.drop_table('proposals')

    op.drop_index(op.f('ix_messages_conversation_id'), table_name='messages')
    op.drop_table('messages')

    op.drop_index(op.f('ix_conversations_user_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_conversation_id'),
                  table_name='conversations')
    op.drop_table('conversations')

    op.drop_index(op.f('ix_api_keys_key_hash'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_user_id'), table_name='api_keys')
    op.drop_table('api_keys')

    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

    op.execute('DROP TYPE IF EXISTS userrole')
