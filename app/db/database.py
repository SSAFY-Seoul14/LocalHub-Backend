from pathlib import Path

from sqlalchemy import Float, Index, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


# 프로젝트 루트: LocalHub-Backend/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# SQLite 파일: LocalHub-Backend/data/localhub.db
DB_PATH = PROJECT_ROOT / "data" / "localhub.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"


class Base(DeclarativeBase):
    """모든 SQLAlchemy 모델이 상속하는 기본 클래스."""


class Place(Base):
    """
    한국관광공사 TourAPI 4.0의 장소 데이터를 저장하는 통합 테이블.

    관광지, 문화시설, 축제공연행사, 여행코스, 레포츠,
    숙박, 쇼핑, 음식점 데이터를 content_type_id로 구분한다.
    """

    __tablename__ = "places"

    # 서비스 내부에서 사용하는 PK
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # TourAPI 원본 식별자
    content_id: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
        index=True,
    )
    content_type_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    # JSON 최상위 메타데이터
    region: Mapped[str] = mapped_column(String(50), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # 장소 기본 정보
    title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    address: Mapped[str] = mapped_column(Text, nullable=False, default="")
    address_detail: Mapped[str] = mapped_column(Text, nullable=False, default="")
    zipcode: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    telephone: Mapped[str] = mapped_column(String(200), nullable=False, default="")

    # 지도 좌표: TourAPI mapx=경도, mapy=위도
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    map_level: Mapped[str] = mapped_column(String(10), nullable=False, default="")

    # 행정구역 코드
    area_code: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    sigungu_code: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    legal_region_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="",
    )
    legal_sigungu_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="",
    )

    # 기존 관광 분류 코드
    category1: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    category2: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    category3: Mapped[str] = mapped_column(String(30), nullable=False, default="")

    # 신규 분류 체계 코드
    classification1: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="",
    )
    classification2: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="",
    )
    classification3: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="",
    )

    # 이미지 및 저작권 정보
    image_url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    thumbnail_url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    copyright_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="",
    )

    # TourAPI 원본 시각. 원본 형식 YYYYMMDDHHmmss를 그대로 보존한다.
    source_created_at: Mapped[str] = mapped_column(
        String(14),
        nullable=False,
        default="",
    )
    source_modified_at: Mapped[str] = mapped_column(
        String(14),
        nullable=False,
        default="",
    )

    # 어느 JSON 파일에서 적재했는지 추적
    source_file: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="",
    )

    __table_args__ = (
        Index("ix_places_type_title", "content_type_id", "title"),
        Index("ix_places_coordinates", "latitude", "longitude"),
        Index(
            "ix_places_legal_area",
            "legal_region_code",
            "legal_sigungu_code",
        ),
    )


# SQLite는 한 요청에서 생성한 연결을 다른 스레드에서도 사용할 수 있도록 설정한다.
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
    """정의된 모든 테이블을 SQLite에 생성한다."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    FastAPI Depends에서 사용할 DB 세션 의존성.

    예:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()