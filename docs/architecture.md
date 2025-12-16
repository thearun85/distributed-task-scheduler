# Task Scheduler Architecture - Version 0.1

┌─────────────────────────────────────────────────────────┐
│                    SINGLE PROCESS                       │
│                                                         │
│   ┌─────────────┐         ┌─────────────────────────┐  │
│   │  Flask API  │         │    Scheduler Loop       │  │
│   │             │         │                         │  │
│   │ POST /tasks │────────►│  1. Poll for due tasks  │  │
│   │ GET /tasks  │         │  2. Execute handler     │  │
│   │             │         │  3. Update state        │  │
│   └─────────────┘         │  4. Sleep, repeat       │  │
│          │                └───────────┬─────────────┘  │
│          │                            │                │
│          ▼                            ▼                │
│   ┌─────────────────────────────────────────────────┐  │
│   │                   PostgreSQL                    │  │
│   │                                                 │  │
│   │  tasks: id, type, payload, state, scheduled_at │  │
│   └─────────────────────────────────────────────────┘  │
└───
