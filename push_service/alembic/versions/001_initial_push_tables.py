"""Initial push service tables

Revision ID: 001
Revises: 
Create Date: 2025-11-13 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create push_notifications table
    op.create_table('push_notifications',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('notification_id', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('template_code', sa.String(), nullable=False),
    sa.Column('variables', sa.JSON(), nullable=True),
    sa.Column('request_id', sa.String(), nullable=False),
    sa.Column('priority', sa.Integer(), nullable=True),
    sa.Column('metadata', sa.JSON(), nullable=True),
    sa.Column('device_token', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('click_url', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('sent_at', sa.DateTime(), nullable=True),
    sa.Column('delivered_at', sa.DateTime(), nullable=True),
    sa.Column('failed_at', sa.DateTime(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('retry_count', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_push_notifications_notification_id'), 'push_notifications', ['notification_id'], unique=True)
    op.create_index(op.f('ix_push_notifications_user_id'), 'push_notifications', ['user_id'], unique=False)
    op.create_index(op.f('ix_push_notifications_request_id'), 'push_notifications', ['request_id'], unique=False)

    # Create push_notification_logs table
    op.create_table('push_notification_logs',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('notification_id', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('metadata', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_push_notification_logs_notification_id'), 'push_notification_logs', ['notification_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_push_notification_logs_notification_id'), table_name='push_notification_logs')
    op.drop_table('push_notification_logs')
    op.drop_index(op.f('ix_push_notifications_request_id'), table_name='push_notifications')
    op.drop_index(op.f('ix_push_notifications_user_id'), table_name='push_notifications')
    op.drop_index(op.f('ix_push_notifications_notification_id'), table_name='push_notifications')
    op.drop_table('push_notifications')