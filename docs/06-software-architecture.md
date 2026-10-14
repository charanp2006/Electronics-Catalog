# 6. Software Architecture

## 6.1 Architecture Overview
Full-stack 3-tier architecture with separation of concerns.

```mermaid
flowchart TB
    A[React.js Frontend - Vite] -->|HTTP/REST/JSON| B[FastAPI Backend]
    B -->|PyMongo Driver| C[MongoDB Database]
    D[MongoDB Atlas - Cloud] -.-> C
    E[Local MongoDB - mongod] --> C
    B --> F[Environment Config .env]
```

## 6.2 Technology Stack

| Layer | Technology | Justification |
|---|---|---|
| Frontend | React.js + Vite + Tailwind CSS | Fast, modern, simple for API integration |
| Backend | FastAPI (Python) | Async, auto docs, clean for MongoDB |
| Database | MongoDB | Document store, flexible schema, demonstrates NoSQL |
| ODM/Driver | PyMongo | Direct control, clear MongoDB usage demonstration |
| API | REST (JSON) | Simple, standard |

## 6.3 Backend Architecture

```mermaid
flowchart TB
    subgraph Backend
        A[API Routes / routers] --> B[Services/Business Logic]
        B --> C[Repositories/DAL]
        C --> D[DB Connection - config/db.py]
        D --> E[MongoDB]
        A --> F[Schemas/Pydantic Models]
        G[.env Config] --> D
    end
```

## 6.4 Project Structure (Planned)

```text
Electronics catalog/
├── backend/
│   ├── app/
│   │   ├── api/v1/         # Route handlers
│   │   ├── core/           # Config, settings
│   │   ├── db/             # MongoDB connection
│   │   ├── models/         # Pydantic schemas
│   │   ├── repositories/   # Data access layer
│   │   ├── services/       # Business logic
│   │   ├── schemas/        # Request/Response models
│   │   ├── utils/          # Helpers
│   │   └── main.py         # FastAPI app
│   ├── .env.example
│   ├── requirements.txt
│   └── seed.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/api.js
│   │   ├── hooks/
│   │   ├── utils/
│   │   └── App.jsx
│   ├── public/
│   └── package.json
├── docs/
├── implementation/
└── README.md
```

## 6.5 Data Flow

```mermaid
sequenceDiagram
    participant UI as React UI
    participant API as FastAPI
    participant Repo as Repository/DAL
    participant DB as MongoDB
    UI->>API: HTTP GET /api/v1/products
    API->>Repo: get_products(filters)
    Repo->>DB: find() with query
    DB-->>Repo: Documents (BSON/JSON)
    Repo-->>API: Processed Data
    API-->>UI: JSON Response
    UI-->>UI: Render Components
```
