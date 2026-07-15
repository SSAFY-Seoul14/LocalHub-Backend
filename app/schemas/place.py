from pydantic import BaseModel, ConfigDict


class PlaceListResponse(BaseModel):
    """
    지도에 표시할 장소 목록 응답
    """

    id: int
    title: str

    latitude: float
    longitude: float

    content_type: str
    image_url: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class PlaceDetailResponse(BaseModel):
    """
    장소 상세 조회 응답
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

    category1: str | None = None
    category2: str | None = None
    category3: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )