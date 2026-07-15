from typing import Literal

from pydantic import BaseModel, Field, model_validator


class RouteCoordinate(BaseModel):
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="위도",
        examples=[37.5666103],
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="경도",
        examples=[126.9783882],
    )


class RouteResponse(BaseModel):
    distance: int = Field(
        ...,
        ge=0,
        description="총 이동 거리(m)",
        examples=[10675],
    )
    duration: int = Field(
        ...,
        ge=0,
        description="예상 이동 시간(초)",
        examples=[1857],
    )
    taxi_fare: int = Field(
        ...,
        ge=0,
        description="예상 택시 요금(원)",
        examples=[14500],
    )
    toll_fare: int = Field(
        ...,
        ge=0,
        description="예상 통행료(원)",
        examples=[0],
    )
    origin: RouteCoordinate = Field(
        ...,
        description="출발지 좌표",
    )
    destination: RouteCoordinate = Field(
        ...,
        description="목적지 좌표",
    )
    path: list[RouteCoordinate] = Field(
        default_factory=list,
        description="전체 경로 Polyline 좌표",
    )


class RoutePlace(BaseModel):
    place_id: int | None = Field(
        default=None,
        description="DB 장소 ID",
        examples=[1],
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="장소 이름",
        examples=["서울시청"],
    )
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="장소 위도",
        examples=[37.5666103],
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="장소 경도",
        examples=[126.9783882],
    )


class MultiRouteRequest(BaseModel):
    places: list[RoutePlace] = Field(
        ...,
        min_length=2,
        max_length=32,
        description=(
            "방문할 장소 목록입니다. "
            "첫 번째 장소는 출발지, 마지막 장소는 목적지로 고정하고 "
            "중간 장소들의 방문 순서를 최적화합니다."
        ),
    )
    priority: Literal[
        "RECOMMEND",
        "TIME",
        "DISTANCE",
    ] = Field(
        default="RECOMMEND",
        description=(
            "길찾기 우선순위입니다. "
            "RECOMMEND는 추천 경로, "
            "TIME은 최단 시간, "
            "DISTANCE는 최단 거리입니다."
        ),
    )

    @model_validator(mode="after")
    def validate_places(self):
        coordinates = {
            (place.latitude, place.longitude)
            for place in self.places
        }

        if len(coordinates) != len(self.places):
            raise ValueError(
                "동일한 좌표의 장소를 중복해서 입력할 수 없습니다."
            )

        return self


class OrderedRoutePlace(RoutePlace):
    order: int = Field(
        ...,
        ge=1,
        description="최적화된 방문 순서",
        examples=[1],
    )
    role: Literal[
        "ORIGIN",
        "WAYPOINT",
        "DESTINATION",
    ] = Field(
        ...,
        description=(
            "경로 내 장소 역할입니다. "
            "ORIGIN은 출발지, "
            "WAYPOINT는 경유지, "
            "DESTINATION은 목적지입니다."
        ),
    )


class RouteSummary(BaseModel):
    distance: int = Field(
        ...,
        ge=0,
        description="전체 이동 거리(m)",
        examples=[16894],
    )
    duration: int = Field(
        ...,
        ge=0,
        description="전체 예상 이동 시간(초)",
        examples=[3782],
    )
    taxi_fare: int = Field(
        ...,
        ge=0,
        description="전체 예상 택시 요금(원)",
        examples=[23800],
    )
    toll_fare: int = Field(
        ...,
        ge=0,
        description="전체 예상 통행료(원)",
        examples=[0],
    )


class RouteLegPlace(BaseModel):
    place_id: int | None = Field(
        default=None,
        description="DB 장소 ID",
    )
    name: str = Field(
        ...,
        description="장소 이름",
    )
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="장소 위도",
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="장소 경도",
    )


class RouteLeg(BaseModel):
    order: int = Field(
        ...,
        ge=1,
        description="구간 순서",
        examples=[1],
    )
    origin: RouteLegPlace = Field(
        ...,
        description="해당 구간의 출발 장소",
    )
    destination: RouteLegPlace = Field(
        ...,
        description="해당 구간의 도착 장소",
    )
    distance: int = Field(
        ...,
        ge=0,
        description="해당 구간의 이동 거리(m)",
        examples=[2310],
    )
    duration: int = Field(
        ...,
        ge=0,
        description="해당 구간의 예상 이동 시간(초)",
        examples=[620],
    )
    path: list[RouteCoordinate] = Field(
        default_factory=list,
        description="해당 구간의 Polyline 좌표",
    )


class MultiRouteResponse(BaseModel):
    optimized: bool = Field(
        default=True,
        description="방문 순서 최적화 적용 여부",
    )
    summary: RouteSummary = Field(
        ...,
        description="전체 경로 요약 정보",
    )
    places: list[OrderedRoutePlace] = Field(
        ...,
        description="최적화된 방문 순서가 포함된 장소 목록",
    )
    legs: list[RouteLeg] = Field(
        ...,
        description="각 장소 사이의 경로 구간 목록",
    )
    full_path: list[RouteCoordinate] = Field(
        default_factory=list,
        description="전체 경로 Polyline 좌표",
    )


class PlaceIdsRouteRequest(BaseModel):
    place_ids: list[int] = Field(
        ...,
        min_length=2,
        max_length=32,
        description=(
            "경로에 포함할 장소 ID 목록입니다. "
            "첫 번째 장소는 출발지, 마지막 장소는 목적지로 고정하고 "
            "중간 장소들의 방문 순서를 최적화합니다."
        ),
        examples=[[15, 27, 81, 130]],
    )
    priority: Literal[
        "RECOMMEND",
        "TIME",
        "DISTANCE",
    ] = Field(
        default="RECOMMEND",
        description="길찾기 우선순위",
    )

    @model_validator(mode="after")
    def validate_place_ids(self):
        if len(set(self.place_ids)) != len(self.place_ids):
            raise ValueError(
                "동일한 place_id를 중복해서 입력할 수 없습니다."
            )

        return self