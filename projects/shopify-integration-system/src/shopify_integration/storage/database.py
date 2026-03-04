"""Database repository for persistent storage."""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Integer,
    String,
    create_engine,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from shopify_integration.config import Settings

Base = declarative_base()


class SyncLog(Base):
    """Synchronization log entry."""

    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True)
    operation = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False)
    items_processed = Column(Integer, default=0)
    items_succeeded = Column(Integer, default=0)
    items_failed = Column(Integer, default=0)
    errors = Column(JSON, default=list)
    details = Column(JSON, default=dict)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class DatabaseRepository:
    """PostgreSQL database repository."""

    def __init__(self, settings: Settings) -> None:
        """Initialize database repository.

        Args:
            settings: Application settings.
        """
        self.settings = settings
        self._engine = None
        self._session_maker = None

    async def connect(self) -> None:
        """Establish database connection."""
        self._engine = create_async_engine(
            self.settings.database_url,
            echo=self.settings.debug,
        )
        self._session_maker = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
        )

        # Create tables
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def disconnect(self) -> None:
        """Close database connection."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_maker = None

    async def log_sync(
        self,
        operation: str,
        status: str,
        items_processed: int = 0,
        items_succeeded: int = 0,
        items_failed: int = 0,
        errors: Optional[list[str]] = None,
        details: Optional[dict[str, Any]] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
    ) -> int:
        """Log synchronization operation.

        Args:
            operation: Operation name.
            status: Operation status.
            items_processed: Number of items processed.
            items_succeeded: Number of items succeeded.
            items_failed: Number of items failed.
            errors: List of error messages.
            details: Additional details.
            started_at: Operation start time.
            completed_at: Operation completion time.

        Returns:
            Log entry ID.
        """
        if not self._session_maker:
            raise RuntimeError("Database not connected")

        async with self._session_maker() as session:
            log = SyncLog(
                operation=operation,
                status=status,
                items_processed=items_processed,
                items_succeeded=items_succeeded,
                items_failed=items_failed,
                errors=errors or [],
                details=details or {},
                started_at=started_at or datetime.utcnow(),
                completed_at=completed_at,
            )
            session.add(log)
            await session.commit()
            return log.id

    async def get_sync_logs(
        self,
        operation: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get synchronization logs.

        Args:
            operation: Filter by operation name.
            limit: Maximum number of logs.

        Returns:
            List of log entries.
        """
        if not self._session_maker:
            raise RuntimeError("Database not connected")

        async with self._session_maker() as session:
            query = select(SyncLog).order_by(SyncLog.created_at.desc()).limit(limit)

            if operation:
                query = query.where(SyncLog.operation == operation)

            result = await session.execute(query)
            logs = result.scalars().all()

            return [
                {
                    "id": log.id,
                    "operation": log.operation,
                    "status": log.status,
                    "items_processed": log.items_processed,
                    "items_succeeded": log.items_succeeded,
                    "items_failed": log.items_failed,
                    "errors": log.errors,
                    "details": log.details,
                    "started_at": log.started_at.isoformat() if log.started_at else None,
                    "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
                for log in logs
            ]
