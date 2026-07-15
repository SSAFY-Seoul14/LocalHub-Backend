from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.place_repository import find_places_by_ids
from app.schemas.map import (
    MultiRouteRequest,
    MultiRouteResponse,
    PlaceIdsRouteRequest,
    RoutePlace,
    RouteResponse,
)
from app.services.kakao_mobility_service import (
    get_directions,
    get_multi_directions,
)

router = APIRouter(
    prefix="/api/maps",
    tags=["maps"],
)


@router.get(
    "/directions/test",
    response_model=RouteResponse,
    summary="카카오 자동차 길찾기 테스트",
)
async def test_kakao_directions(
    origin_longitude: float = Query(
        126.9783882,
        description="출발지 경도",
    ),
    origin_latitude: float = Query(
        37.5666103,
        description="출발지 위도",
    ),
    destination_longitude: float = Query(
        127.027621,
        description="목적지 경도",
    ),
    destination_latitude: float = Query(
        37.497942,
        description="목적지 위도",
    ),
) -> RouteResponse:
    return await get_directions(
        origin_longitude=origin_longitude,
        origin_latitude=origin_latitude,
        destination_longitude=destination_longitude,
        destination_latitude=destination_latitude,
    )

@router.post(
    "/routes",
    response_model=MultiRouteResponse,
    summary="여러 장소 자동차 경로 생성",
    description=(
        "첫 번째 장소를 출발지, 마지막 장소를 목적지, "
        "중간 장소들을 경유지로 사용해 자동차 경로를 생성합니다."
    ),
)
async def create_multi_route(
    request: MultiRouteRequest,
) -> MultiRouteResponse:
    return await get_multi_directions(request)