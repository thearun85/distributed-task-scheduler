# Distributed Task Scheduler
A production-grade task scheduler demonstrating distributed system concepts.

## Core Stack

| Layer | Technology | Version |
|-------|------------|---------|
| **Language** | Python | 3.12 |
| **API Framework** | Flask | 3.1.1 |
| **Database** | PostgreSQL | 16 |
| **ORM** | SQLAlchemy | 2.0 |
| **Migrations** | Alembic | (from Phase 2) |
| **Background threads** | Python `threading` | stdlib |
| **Container** | Docker | latest |
| **Orchestration** | Docker Swarm | (Phase 5) |
| **Metrics** | Prometheus | (Phase 6) |
| **Dashboard** | Grafana | (Phase 6) |

## Running Locally
```bash
docker compose up --build
```

## Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Check the status of URL shortener |
| POST | /tasks | Create a new task for execution |
| GET | /tasks | List all tasks |
| GET | /tasks/<task_id> | Get a task by id |
| GET | /tasks/stats | Display stats for the tasks by state |

**Health check API:**

```bash
curl http://localhost:5000/health
```
Expected Output:
```json
{
  "service": "distributed-scheduler",
  "status": "healthy",
  "timestamp": "2025-12-16T05:23:13.889672Z"
}
```

**Create Task API:**

```bash
curl -X POST http://localhost:5000/tasks \
-H "Content-Type: application/json" \
-d '{"task_type":"TEST"}'
```
Expected Output:
```json
{
  "attempts": 0,
  "created_at": "2025-12-16T05:29:13.404750Z",
  "id": 1,
  "max_attempts": 3,
  "payload": {},
  "scheduled_at": "2025-12-16T05:29:13.404728Z",
  "state": "PENDING",
  "task_type": "TEST"
}
```

**List all Tasks:**

```bash
curl http://localhost:5000/tasks
```
Expected Output:
```json
"tasks": [
    {
      "attempts": 0,
      "created_at": "2025-12-16T05:29:13.404750Z",
      "id": 1,
      "max_attempts": 3,
      "payload": {},
      "scheduled_at": "2025-12-16T05:29:13.404728Z",
      "state": "PENDING",
      "task_type": "TEST"
    }
   ]
```

**Get a Task by ID:**

```bash
curl http://localhost:5000/tasks/1
```
Expected Output:
```json
{
     "attempts": 0,
     "created_at": "2025-12-16T05:29:13.404750Z",
     "id": 1,
     "max_attempts": 3,
     "payload": {},
     "scheduled_at": "2025-12-16T05:29:13.404728Z",
     "state": "PENDING",
     "task_type": "TEST"
   }
```

**Get the Task Stats:**

```bash
curl http://localhost:5000/tasks/stats
```
Expected Output:
```json
{
     "by_state": {
       "PENDING": 3
     },
     "total": 3
   }
```


## Teardown Application
```bash
docker compose down -v
```
