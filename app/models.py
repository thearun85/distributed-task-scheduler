from __future__ import annotations
import enum
from sqlalchemy import BigInteger, String, DateTime, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.db import Base

class TaskState(enum.Enum):
    PENDING = 'PENDING'
    CLAIMED = 'CLAIMED'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    DEAD = 'DEAD'

class Task(Base):

    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    task_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    
    state: Mapped[TaskState] = mapped_column(nullable=False, default=TaskState.PENDING)
    
    attempts: Mapped[int] = mapped_column(nullable=False, server_default="0")
    max_attempts: Mapped[int] = mapped_column(nullable=False, server_default="3")
    last_error: Mapped[str|None] = mapped_column(Text, nullable=True)
    idempotency_key: Mapped[str|None] = mapped_column(String(128), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    __table_args__ = (
        Index("idx_tasks_pending", "scheduled_at", postgresql_where=
        (state=="PENDING")),
        Index("idx_tasks_state", "state"),
     )

    def to_dict(self)->dict:

        return {
            "id": self.id,
            "task_type": self.task_type,
            "payload": self.payload,
            "scheduled_at": self.scheduled_at.isoformat() + "Z" if self.scheduled_at else None,
            "state": self.state.value,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "last_error": self.last_error,
            "idempotency_key": self.idempotency_key,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
