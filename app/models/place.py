from sqlalchemy import Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Place(Base):
    """
    한국관광공사 TourAPI 4.0의 장소 데이터를 저장하는 통합 테이블.

    관광지, 문화시설, 축제공연행사, 여행코스, 레포츠,
    숙박, 쇼핑, 음식점 데이터를 content_type_id로 구분한다.
    """

    __tablename__ = "places"

    # LocalHub 서비스 내부에서 사용하는 기본키
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

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
    region: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    content_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # 장소 기본 정보
    title: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        index=True,
    )

    address: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    address_detail: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    zipcode: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="",
    )

    telephone: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        default="",
    )

    # TourAPI mapx는 경도, mapy는 위도
    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    map_level: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="",
    )

    # 행정구역 코드
    area_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="",
    )

    sigungu_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="",
    )

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
    category1: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="",
    )

    category2: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="",
    )

    category3: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="",
    )

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
    image_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    thumbnail_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    copyright_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="",
    )

    # TourAPI의 YYYYMMDDHHmmss 문자열을 원본 그대로 보존
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

    # 데이터를 가져온 JSON 파일명
    source_file: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="",
    )

    __table_args__ = (
        Index(
            "ix_places_type_title",
            "content_type_id",
            "title",
        ),
        Index(
            "ix_places_coordinates",
            "latitude",
            "longitude",
        ),
        Index(
            "ix_places_legal_area",
            "legal_region_code",
            "legal_sigungu_code",
        ),
    )