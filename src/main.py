"""
TeenFreelance Backend API
Enterprise-level FastAPI application with Clean Architecture
"""
from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
import os
import uvicorn
import time
from contextlib import asynccontextmanager

# Импорты конфигурации и безопасности
from src.config import settings
from src.presentation.api.v1.router import router as api_router
from src.infrastructure.repositiry.base_repository import engine
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from src.infrastructure.security.rate_limiter import RateLimitMiddleware
from src.infrastructure.monitoring.logger import logger, audit_logger, security_logger
from src.infrastructure.di.container import container, service_provider
from src.infrastructure.cache.memory_cache import memory_cache
from src.infrastructure.cache.redis_client import close_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    logger.info("Starting TeenFreelance API", version=settings.app_version)
    
    # Проверка подключения к БД и создание таблиц
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda _: None)
        logger.info("Database connection established")
        
        # Создание таблиц если их нет
        from src.infrastructure.repositiry.db_models import Base
        async with engine.begin() as conn:
            def _create_all(sync_conn):
                try:
                    Base.metadata.create_all(sync_conn, checkfirst=True)
                except OperationalError as exc:  # pragma: no cover
                    if getattr(exc.orig, "args", [None])[0] == 1050:
                        logger.warning("Database tables already exist; skipping creation", error=str(exc))
                    else:
                        raise
            await conn.run_sync(_create_all)

        if settings.database_url.startswith("mysql"):
            async with engine.begin() as conn:
                await _ensure_mysql_columns(conn)
        logger.info("Database tables verified/created")
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        raise
    
    # Инициализация кэша
    logger.info("Memory cache initialized", stats=memory_cache.get_stats())
    
    yield
    
    # Shutdown
    logger.info("Shutting down TeenFreelance API")
    memory_cache.clear()
    await close_redis_client()


async def _ensure_mysql_columns(conn):
    required_columns = {
        "users": {
            "rub_balance": "FLOAT DEFAULT 0.0 NOT NULL",
            "is_editor": "BOOL DEFAULT FALSE NOT NULL",
        },
    }
    for table, columns in required_columns.items():
        for column, definition in columns.items():
            result = await conn.execute(
                text("SHOW COLUMNS FROM `{table}` LIKE :column".format(table=table)),
                {"column": column},
            )
            if result.first() is None:
                await conn.execute(
                    text(
                        "ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}".format(
                            table=table, column=column, definition=definition
                        )
                    )
                )


# Создание FastAPI приложения
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Enterprise-level freelance platform for teenagers",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware для безопасности
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "testserver", "*.teenfreelance.ru"]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate limiting
app.middleware("http")(RateLimitMiddleware(settings.rate_limit_requests, settings.rate_limit_window))

# Статические файлы
import os
assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Middleware для логирования запросов"""
    start_time = time.time()
    
    # Логирование входящего запроса
    logger.info(
        f"Request: {request.method} {request.url.path}",
        ip_address=request.client.host,
        endpoint=request.url.path,
        method=request.method
    )
    
    # Обработка запроса
    response = await call_next(request)
    
    # Логирование ответа
    process_time = time.time() - start_time
    logger.performance(
        f"Response: {request.method} {request.url.path}",
        duration=process_time,
        status_code=response.status_code,
        ip_address=request.client.host
    )
    
    # Добавление заголовков производительности
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


@app.get("/health")
async def health_check():
    """Health check endpoint для мониторинга"""
    cache_stats = memory_cache.get_stats()
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": time.time(),
        "cache": {
            "items_count": cache_stats["items_count"],
            "hit_rate": cache_stats["hit_rate_percent"],
            "size_mb": cache_stats["size_mb"]
        }
    }


@app.get("/", include_in_schema=False)
async def root():
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    return RedirectResponse(url=frontend_url)

# Обработчики исключений
@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    """Универсальный обработчик исключений"""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        ip_address=request.client.host,
        endpoint=request.url.path
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "error_id": f"ERR_{int(time.time())}"
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Обработчик HTTP исключений"""
    detail_msg = str(exc.detail) if exc.detail else "Unknown error"
    logger.warning(
        f"HTTP exception: {exc.status_code}",
        status_code=exc.status_code,
        detail=detail_msg,
        ip_address=request.client.host,
        endpoint=request.url.path
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": detail_msg, "detail": detail_msg},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации"""
    logger.warning(
        "Validation error",
        errors=exc.errors(),
        ip_address=request.client.host,
        endpoint=request.url.path
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "message": "Validation error",
            "details": exc.errors()
        },
    )


# API роуты (подключаем в конце, чтобы не конфликтовать с документацией)
app.include_router(api_router)

# Backward-compatible auth endpoints without versioned prefix
from src.presentation.api.v1.auth import refresh_tokens, logout  # noqa: E402
app.add_api_route("/auth/refresh", refresh_tokens, methods=["POST"])
app.add_api_route("/auth/logout", logout, methods=["POST"])

if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host='0.0.0.0',
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

