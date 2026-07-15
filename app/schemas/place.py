from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlaceBase(BaseModel):
    """
    장소 공통 응답 필드
    """

    id: int

    content_id: str
    content_type_id: int

    region: str
    content_type: str

    title: str

    address: str | None = None
    address_detail: str | None = None
    zipcode: str | None = None

    telephone: str | None = None

    latitude: float | None = None
    longitude: float | None = None

    image_url: str | None = None
    thumbnail_url: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class PlaceListResponse(PlaceBase):
    """
    장소 목록 및 지도 마커 응답

    목록 조회에서는 응답 크기를 줄이기 위해
    프로그램 설명 등 긴 상세 필드는 제외한다.
    """

    event_start_date: str | None = None
    event_end_date: str | None = None
    event_place: str | None = None


class PlaceDetailResponse(PlaceBase):
    """
    장소 상세 조회 응답
    """

    map_level: str | None = None

    # 지역 코드
    area_code: str | None = None
    sigungu_code: str | None = None
    legal_region_code: str | None = None
    legal_sigungu_code: str | None = None

    # 관광 분류
    category1: str | None = None
    category2: str | None = None
    category3: str | None = None

    classification1: str | None = None
    classification2: str | None = None
    classification3: str | None = None

    # 저작권
    copyright_type: str | None = None

    # 축제·공연·행사 정보
    event_start_date: str | None = None
    event_end_date: str | None = None
    event_place: str | None = None

    play_time: str | None = None
    program: str | None = None
    sub_event: str | None = None

    # 주최 및 주관
    sponsor1: str | None = None
    sponsor1_telephone: str | None = None

    sponsor2: str | None = None
    sponsor2_telephone: str | None = None

    # 예약 및 홈페이지
    event_homepage: str | None = None
    booking_place: str | None = None

    # 관람 정보
    age_limit: str | None = None
    festival_grade: str | None = None
    place_info: str | None = None
    spend_time_festival: str | None = None
    discount_info_festival: str | None = None
    use_time_festival: str | None = None

    # 데이터 출처
    source_created_at: str | None = None
    source_modified_at: str | None = None
    source_file: str | None = None

    # 서비스 생성 및 수정 시각
    created_at: datetime
    updated_at: datetime