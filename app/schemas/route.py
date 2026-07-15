from pydantic import BaseModel, Field


class RouteRequest(BaseModel):
    """
    최적 경로 생성 요청 스키마.
    """

    place_ids: list[int] = Field(
        ...,
        min_length=2,
        max_length=8,
        description="경로를 생성할 장소 ID 목록",
        examples=[[12, 35, 81, 102]],
    )


class RouteCoordinate(BaseModel):
    """
    경로를 구성하는 좌표 스키마.
    """

    latitude: float
    longitude: float


class RoutePlaceResponse(BaseModel):
    """
    최적 방문 경로에 포함된 장소 응답 스키마.
    """

    order: int
    place_id: int
    title: str
    content_type: str
    latitude: float
    longitude: float
    address: str | None = None


class RouteSummaryResponse(BaseModel):
    """
    실제 도로 경로 요약 정보 스키마.
    """

    total_distance: int = Field(
        ...,
        description="전체 이동 거리, 단위는 미터",
    )

    total_duration: int = Field(
        ...,
        description="전체 예상 이동 시간, 단위는 초",
    )

    polyline: list[RouteCoordinate]

class RouteSegmentResponse(BaseModel):
    """
    두 장소 사이의 실제 도로 경로 응답 스키마.
    """

    order: int
    from_place_id: int
    to_place_id: int

    distance: int = Field(
        ...,
        description="구간 이동 거리, 단위는 미터",
    )

    duration: int = Field(
        ...,
        description="구간 예상 이동 시간, 단위는 초",
    )

    polyline: list[RouteCoordinate]


class RouteResponse(BaseModel):
    """
    최적 경로 생성 결과 응답 스키마.
    """

    places: list[RoutePlaceResponse]
    segments: list[RouteSegmentResponse]

    total_distance: int = Field(
        ...,
        description="전체 이동 거리, 단위는 미터",
    )

    total_duration: int = Field(
        ...,
        description="전체 예상 이동 시간, 단위는 초",
    )
    

class RoutePlaceLookupResponse(BaseModel):
    """
    경로 생성 전 장소 조회 결과 응답 스키마.
    """

    order: int
    place_id: int
    title: str
    content_type: str
    latitude: float
    longitude: float
    address: str | None = None


class RoutePlaceLookupListResponse(BaseModel):
    """
    경로 생성 요청에 포함된 장소 목록 응답 스키마.
    """

    places: list[RoutePlaceResponse]