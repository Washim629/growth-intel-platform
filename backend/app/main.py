import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.database import init_db
from app.utils.logging import setup_logging

from app.api import auth, datasets, analysis, kpis, funnel, segments, trends, anomalies, ai, experiments, reports

setup_logging()
logger = logging.getLogger("app.main")
settings = get_settings()

app = FastAPI(
    title="AI-Powered Growth & Lead Intelligence Platform",
    description="Upload lead/customer data and get automatic cleaning, segmentation, "
                "funnel analysis, KPIs, anomaly detection, and AI-generated growth insights.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000, 1)
    logger.info("%s %s -> %s (%sms)", request.method, request.url.path, response.status_code, duration_ms)
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Consistent, useful error shape instead of leaking stack traces.
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred. Please try again."})


@app.on_event("startup")
def on_startup():
    logger.info("Starting up in %s mode (LLM enabled: %s)", settings.ENVIRONMENT, settings.llm_enabled)
    init_db()


@app.get("/")
def root():
    return {
        "product": "AI-Powered Growth & Lead Intelligence Platform",
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    return {"status": "healthy"}


app.include_router(auth.router)
app.include_router(datasets.router)
app.include_router(analysis.router)
app.include_router(kpis.router)
app.include_router(funnel.router)
app.include_router(segments.router)
app.include_router(trends.router)
app.include_router(anomalies.router)
app.include_router(ai.router)
app.include_router(experiments.router)
app.include_router(reports.router)
