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

    일반 장소 정보와 축제·공연·행사 상세 정보를 함께 저장합니다.
    축제 전용 컬럼은 축제 데이터가 아닌 경우 NULL로 저장됩니다.
    """

    __tablename__ = "places"

    # 내부 PK
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # TourAPI 원본 정보
    content_id = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    content_type_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    region = Column(
        String(50),
        nullable=False,
        index=True,
    )

    content_type = Column(
        String(50),
        nullable=False,
        index=True,
    )

    # 장소 기본 정보
    title = Column(
        String(255),
        nullable=False,
        index=True,
    )

    # 주소
    address = Column(
        String(500),
        nullable=True,
    )

    address_detail = Column(
        String(500),
        nullable=True,
    )

    zipcode = Column(
        String(20),
        nullable=True,
    )

    # 연락처
    telephone = Column(
        String(255),
        nullable=True,
    )

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

    map_level = Column(
        String(20),
        nullable=True,
    )

    # 지역 코드
    area_code = Column(
        String(20),
        nullable=True,
    )

    sigungu_code = Column(
        String(20),
        nullable=True,
    )

    legal_region_code = Column(
        String(20),
        nullable=True,
    )

    legal_sigungu_code = Column(
        String(20),
        nullable=True,
    )

    # 관광 분류
    category1 = Column(
        String(20),
        nullable=True,
    )

    category2 = Column(
        String(20),
        nullable=True,
    )

    category3 = Column(
        String(20),
        nullable=True,
    )

    classification1 = Column(
        String(20),
        nullable=True,
    )

    classification2 = Column(
        String(20),
        nullable=True,
    )

    classification3 = Column(
        String(20),
        nullable=True,
    )

    # 이미지
    image_url = Column(
        Text,
        nullable=True,
    )

    thumbnail_url = Column(
        Text,
        nullable=True,
    )

    # 저작권
    copyright_type = Column(
        String(20),
        nullable=True,
    )

    # =========================================================
    # 축제·공연·행사 상세 정보
    # content_type_id가 15인 데이터에서 주로 사용됩니다.
    # =========================================================

    # 행사 시작일 / 종료일
    # TourAPI 원본 형식: YYYYMMDD
    event_start_date = Column(
        String(8),
        nullable=True,
        index=True,
    )

    event_end_date = Column(
        String(8),
        nullable=True,
        index=True,
    )

    # 행사 장소
    event_place = Column(
        String(500),
        nullable=True,
    )

    # 공연 및 운영 시간
    play_time = Column(
        Text,
        nullable=True,
    )

    # 주요 프로그램
    program = Column(
        Text,
        nullable=True,
    )

    # 부대 행사
    sub_event = Column(
        Text,
        nullable=True,
    )

    # 주최자 및 연락처
    sponsor1 = Column(
        String(255),
        nullable=True,
    )

    sponsor1_telephone = Column(
        String(255),
        nullable=True,
    )

    # 주관자 및 연락처
    sponsor2 = Column(
        String(255),
        nullable=True,
    )

    sponsor2_telephone = Column(
        String(255),
        nullable=True,
    )

    # 행사 홈페이지
    event_homepage = Column(
        Text,
        nullable=True,
    )

    # 예매처
    booking_place = Column(
        Text,
        nullable=True,
    )

    # 관람 가능 연령
    age_limit = Column(
        String(255),
        nullable=True,
    )

    # 축제 등급
    festival_grade = Column(
        String(100),
        nullable=True,
    )

    # 행사장 정보
    place_info = Column(
        Text,
        nullable=True,
    )

    # 관람 소요 시간
    spend_time_festival = Column(
        String(255),
        nullable=True,
    )

    # 할인 정보
    discount_info_festival = Column(
        Text,
        nullable=True,
    )

    # 이용 요금
    use_time_festival = Column(
        Text,
        nullable=True,
    )

    # TourAPI 원본 시간
    source_created_at = Column(
        String(20),
        nullable=True,
    )

    source_modified_at = Column(
        String(20),
        nullable=True,
    )

    # 적재 파일명
    source_file = Column(
        String(255),
        nullable=True,
    )

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