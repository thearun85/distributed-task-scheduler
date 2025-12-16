from flask import Blueprint, jsonify, request
from datetime import datetime

from sqlalchemy import func
from app.repository import TaskRepository, DuplicateIdempotencyKeyError

api_bp = Blueprint("api", __name__)

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

    try:
        task = TaskRepository.create(
            task_type=data['task_type'],
            payload = data.get('payload', {}),
            scheduled_at = scheduled_at,
            max_attempts = data.get('max_attempts', 3),
            idempotency_key = data.get('idempotency_key'),
        )
        return jsonify(task.to_dict()), 201
    except DuplicateIdempotencyKeyError as e:
        return jsonify({
            "error": "Duplicate idempotency key"
        }), 409    

@api_bp.route("/tasks", methods=["GET"])
def list_tasks():
    results = TaskRepository.get_all()
    return jsonify({
        "tasks": [t.to_dict() for t in results],
        "total": len(results),
    })
    

@api_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id: int):
    task = TaskRepository.get_by_id(task_id)
    if not task:
        return jsonify({
            "error": "Task not found"
        }), 404
    return jsonify(task.to_dict())

@api_bp.route("/tasks/stats", methods=["GET"])
def task_stats():
    return jsonify(TaskRepository.get_stats())

    
