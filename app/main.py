from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.routes import health, posts
from app.db.database import init_db

from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    FastAPI 애플리케이션 시작 및 종료 시 실행되는 함수

    서버가 시작될 때 SQLAlchemy 모델을 확인하고,
    존재하지 않는 DB 테이블을 생성한다.
    """

    init_db()

    yield


app = FastAPI(
    title="LocalHub API",
    description="서울 관광 데이터와 익명 게시판을 제공하는 LocalHub 백엔드 API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health.router)
app.include_router(posts.router)


@app.get(
    "/",
    tags=["Root"],
    summary="API 기본 정보",
)

def read_root() -> dict[str, str]:
    """
    LocalHub API 기본 상태를 반환한다.
    """

    return {
        "message": "LocalHub API",
        "docs": "/docs",
    }