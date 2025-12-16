from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from app.db import get_session
from app.models import Task
from datetime import datetime

class DuplicateIdempotencyKeyError(Exception):
    pass

class TaskRepository:

    @staticmethod
    def create(
        task_type: str,
        payload: dict | None= None,
        scheduled_at: datetime | None = None,
        max_attempts: int=3,
        idempotency_key: str | None = None,
    ) -> Task:

        session = get_session()
        try:
            task = Task(
                task_type=task_type,
                payload=payload or {},
                scheduled_at = scheduled_at or datetime.utcnow(),
                max_attempts=max_attempts,
                idempotency_key=idempotency_key,
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            return task
        
        except IntegrityError:
            session.rollback()
            raise DuplicateIdempotencyKeyError(f"Duplicate idempotency_key: {idempotency_key}")
        finally:
            session.close()

    @staticmethod
    def get_all():
        session = get_session()
        try:
            return session.query(Task).order_by(Task.created_at.desc()).limit(100).all()
            
        finally:
            session.close()

    @staticmethod
    def get_by_id(task_id: int)->Task:
        session = get_session()
        try:
            return session.query(Task).filter(Task.id==task_id).first()
        finally:
            session.close()
            
    @staticmethod
    def get_stats()->dict:
        session = get_session()
        try:
            tasks = session.query(Task.state, func.count(Task.id)).group_by(Task.state).all()
            stats = {state.value:  count for state, count in tasks}
            return {
                "by_state": stats,
                "total": sum(stats.values()),
            }
        finally:
            session.close()

    @staticmethod
    def get_due_tasks(limit: int=10)->list[Task]:
        session = get_session()
        try:
            return session.query(Task).filter(Task.state == TaskState.PENDING).filter(Task.scheduled_at<=datetime.utcnow()).order_by(Task.scheduled_at).limit(limit).all()

        finally:
            session.close()
