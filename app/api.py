from flask import Blueprint, jsonify, request
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from app.db import get_session
from app.models import Task, TaskState

api_bp = Blueprint("api", __name__)

_next_id = 1
_tasks = {}

@api_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "distributed-scheduler",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

@api_bp.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json() or {}
    
    if "task_type" not in data:
        return jsonify({
            "error": "task_type is a required field"
        }), 400

    scheduled_at = datetime.utcnow()
    
    if "scheduled_at" in data:
        try:
            scheduled_at = datetime.fromisoformat(data['scheduled_at'].replace("Z", '00:00'))
            scheduled_at = scheduled_at.replace(tzinfo=None)
        except ValueError as e:
            return jsonify({
                "error": "Invalid scheduled_at format "
            }), 400
            
    task = Task(
        task_type=data['task_type'],
        payload = data.get('payload', {}),
        scheduled_at = scheduled_at,
        max_attempts = data.get('max_attempts', 3),
        idempotency_key = data.get('idempotency_key'),
    )

    session = get_session()

    try:
        session.add(task)
        session.commit()
        session.refresh(task)
        return jsonify(task.to_dict()), 201

    except IntegrityError as e:
        session.rollback()
        return jsonify({
            "error": "Duplicate idempotency key"
        }), 409    
    finally:
        session.close()

    

@api_bp.route("/tasks", methods=["GET"])
def list_tasks():
    session = get_session()
    try:
        results = session.query(Task).order_by(Task.created_at.desc()).limit(100).all()
        return jsonify({
            "tasks": [t.to_dict() for t in results],
            "total": len(results),
        })
    finally:
        session.close()
    

@api_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id: int):
    session = get_session()
    try:
        task = session.query(Task).filter_by(id=task_id).first()
        if not task:
            return jsonify({
                "error": "Task not found"
            }), 404
        return jsonify(task.to_dict())
    finally:
        session.close()

    

@api_bp.route("/tasks/stats", methods=["GET"])
def task_stats():
    session = get_session()
    try:
        results = session.query(Task.state, func.count(Task.id)).group_by(Task.state).all()
        stats = {state.value: count for state, count in results}
        
        return jsonify({
                "by_state": stats,
                "total": sum(stats.values()),
            })
    finally:
        session.close()

    
