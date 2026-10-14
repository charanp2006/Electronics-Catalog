# Implementation Plan - 04: FastAPI Backend Setup

## Objectives
- Initialize FastAPI app
- MongoDB connection layer
- Repository pattern (DAL)
- Core API endpoints

## Tasks

1. **Setup Environment**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn[standard] pymongo python-dotenv pydantic-settings python-multipart
pip freeze > requirements.txt
```

2. **Project Structure** (as per architecture)
- app/core/config.py
- app/db/mongodb.py
- app/schemas/product.py
- app/repositories/product.py
- app/api/v1/products.py
- app/main.py

3. **Config & DB**
- Pydantic settings for env
- MongoDB client singleton
- Get DB instance

4. **Schemas (Pydantic)**
- ProductBase, ProductList, ProductDetail
- Brand, Category, Spec, Review

5. **Repository/DAL**
- Abstract data access
- CRUD + filters + search + sort + pagination

6. **API Routes**
- GET /products (with filters)
- GET /products/{slug}
- GET /categories
- GET /brands
- Health check

7. **CORS**
- Configure for http://localhost:5173

8. **Test**
- Swagger UI /docs
- curl endpoints
