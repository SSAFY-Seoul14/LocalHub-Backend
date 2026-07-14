from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "localhub.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"


class Base(DeclarativeBase):
    """
    모든 SQLAlchemy ORM 모델이 상속받는 기본 클래스
    """

    pass


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
)


SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI 요청마다 DB 세션을 생성하고,
    요청 처리가 끝나면 세션을 닫는다.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    등록된 SQLAlchemy 모델을 기준으로
    존재하지 않는 테이블을 생성한다.
    """

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Place와 Post 모델을 Base.metadata에 등록한다.
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)