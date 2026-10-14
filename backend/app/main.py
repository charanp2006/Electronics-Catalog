from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, brands, cart, categories, orders, products, wishlist
from app.core.config import settings
from app.db.mongodb import close_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    close_client()


app = FastAPI(
    title="ElectroHub NoSQL API",
    version="1.0.0",
    description="Electronics catalog API backed by MongoDB.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix=settings.API_V1_PREFIX)
app.include_router(categories.router, prefix=settings.API_V1_PREFIX)
app.include_router(brands.router, prefix=settings.API_V1_PREFIX)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(cart.router, prefix=settings.API_V1_PREFIX)
app.include_router(wishlist.router, prefix=settings.API_V1_PREFIX)
app.include_router(orders.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Health"])
def root():
    return {"message": "ElectroHub NoSQL API is running", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "env": settings.ENV}
