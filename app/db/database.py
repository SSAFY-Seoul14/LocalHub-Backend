from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# 프로젝트 루트: LocalHub-Backend/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# SQLite 파일 위치: LocalHub-Backend/data/localhub.db
DB_PATH = PROJECT_ROOT / "data" / "localhub.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"


class Base(DeclarativeBase):
    """모든 SQLAlchemy 모델이 상속하는 기본 클래스."""


# FastAPI는 요청을 여러 스레드에서 처리할 수 있으므로
# SQLite의 check_same_thread 옵션을 False로 설정한다.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def init_db() -> None:
    """
    SQLAlchemy 모델을 불러온 뒤 정의된 테이블을 생성한다.

    모델이 먼저 import되어야 Base.metadata가 해당 테이블을 인식한다.
    """
    from app.models import Place  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI Depends에서 사용할 DB 세션 의존성.

    요청이 끝나면 세션을 자동으로 종료한다.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()