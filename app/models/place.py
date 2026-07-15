from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    func,
)

from app.db.database import Base


class Place(Base):
    """
    TourAPI 장소 정보
    """

    __tablename__ = "places"

    # 내부 PK
    id = Column(Integer, primary_key=True, index=True)

    # TourAPI 원본 정보
    content_id = Column(String(30), unique=True, nullable=False, index=True)
    content_type_id = Column(Integer, nullable=False)

    region = Column(String(50), nullable=False)
    content_type = Column(String(50), nullable=False)

    # 장소 기본 정보
    title = Column(String(255), nullable=False)

    # 주소
    address = Column(String(255))
    address_detail = Column(String(255))
    zipcode = Column(String(20))

    # 연락처
    telephone = Column(String(100))

    # 위치 정보
    latitude = Column(
        Float,
        nullable=True,
        index=True,
    )

    longitude = Column(
        Float,
        nullable=True,
        index=True,
    )
    map_level = Column(String(20))

    # 지역 코드
    area_code = Column(String(20))
    sigungu_code = Column(String(20))

    legal_region_code = Column(String(20))
    legal_sigungu_code = Column(String(20))

    # 관광 분류
    category1 = Column(String(20))
    category2 = Column(String(20))
    category3 = Column(String(20))

    classification1 = Column(String(20))
    classification2 = Column(String(20))
    classification3 = Column(String(20))

    # 이미지
    image_url = Column(Text)
    thumbnail_url = Column(Text)

    # 저작권
    copyright_type = Column(String(20))

    # TourAPI 원본 시간
    source_created_at = Column(String(20))
    source_modified_at = Column(String(20))

    # 적재 파일명
    source_file = Column(String(255))

    # 서비스 생성/수정 시간
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )