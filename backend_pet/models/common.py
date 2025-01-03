import sqlalchemy as sa


class HasTimestamp:
    """Timestamp columns for SQLAlchemy models."""

    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now())
    updated_at = sa.Column(
        sa.TIMESTAMP,
        server_default=sa.func.now(),
        onupdate=sa.func.current_timestamp(),
    )
