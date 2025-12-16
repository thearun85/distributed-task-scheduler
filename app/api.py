from flask import Flask, jsonify, request, Blueprint
from datetime import datetime

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
    global _next_id, _tasks
    data = request.get_json() or {}
    
    if "task_type" not in data:
        return jsonify({
            "error": "task_type is a required field"
        }), 400

    task = {
        "id": _next_id,
        "task_type": data["task_type"],
        "payload": data.get("payload", {}),
        "state": "PENDING",
        "scheduled_at": data.get("scheduled_at", datetime.utcnow().isoformat() + "Z"),
        "attempts": 0,
        "max_attempts": data.get("max_attempts", 3),
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    _tasks[_next_id] = task
    _next_id+=1

    return jsonify(task), 201

@api_bp.route("/tasks", methods=["GET"])
def list_tasks():
    global  _tasks
    return jsonify({
        "tasks": list(_tasks.values()),
        "total": len(_tasks),
    })

@api_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id: int):
    global  _tasks
    task = _tasks.get(task_id)
    if not task:
        return jsonify({
            "error": "Task not found"
        }), 404

    return jsonify(task)

@api_bp.route("/tasks/stats", methods=["GET"])
def task_stats():
    global  _tasks
    stats = {}
    for task in _tasks.values():
        state = task["state"]
        stats[state] = stats.get(state, 0) +1

    return jsonify({
        "by_state": stats,
        "total": len(_tasks),
    })
