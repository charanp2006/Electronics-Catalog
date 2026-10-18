from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import auth, brands, cart, categories, orders, products, wishlist
from app.api.v1 import admin as admin_api
from app.core.config import settings
from app.db.mongodb import close_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    close_client()


app = FastAPI(
    title="ElectroHub API",
    version="1.0.0",
    description="ElectroHub — catalog, pricing, cart and orders API.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    response.headers.setdefault("X-Permitted-Cross-Domain-Policies", "none")
    response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
    return response


app.include_router(products.router, prefix=settings.API_V1_PREFIX)
app.include_router(categories.router, prefix=settings.API_V1_PREFIX)
app.include_router(brands.router, prefix=settings.API_V1_PREFIX)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(cart.router, prefix=settings.API_V1_PREFIX)
app.include_router(wishlist.router, prefix=settings.API_V1_PREFIX)
app.include_router(orders.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_api.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Health"])
def root():
    return {"message": "ElectroHub API is running", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "env": settings.ENV}


# Option A: server-rendered admin — mounted once, under /admin only.
from app.admin.routes import router as admin_html_router  # noqa: E402

app.mount(
    "/admin/static",
    StaticFiles(directory=str(Path(__file__).resolve().parent / "admin" / "static")),
    name="admin_static",
)
app.include_router(admin_html_router, prefix="/admin", include_in_schema=False)
