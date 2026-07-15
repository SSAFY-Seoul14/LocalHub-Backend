from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.map import (
    MultiRouteRequest,
    MultiRouteResponse,
    RoutePlace,
)
from app.schemas.route import RouteRequest
from app.services.kakao_mobility_service import get_multi_directions
from app.services.route_service import get_route_places


router = APIRouter(
    prefix="/api/routes",
    tags=["Routes"],
)


@router.post(
    "/optimize",
    response_model=MultiRouteResponse,
    summary="선택한 장소의 최적 자동차 경로 생성",
    description=(
        "선택한 장소 ID 목록을 DB에서 조회한 뒤, "
        "첫 번째 장소만 출발지로 고정하고 "
        "나머지 모든 장소의 방문 순서를 최적화합니다. "
        "최적화 결과의 마지막 장소를 자동 목적지로 설정한 뒤 "
        "카카오모빌리티 길찾기 API를 호출합니다."
    ),
)
async def optimize_route(
    request: RouteRequest,
    db: Session = Depends(get_db),
) -> MultiRouteResponse:
    """
    선택한 장소 ID를 이용해 최적 자동차 경로를 생성합니다.

    처리 순서:
    1. 장소 ID 검증 및 DB 조회
    2. DB Place 모델을 RoutePlace DTO로 변환
    3. 첫 번째 장소를 출발지로 고정
    4. 나머지 모든 장소의 방문 순서 최적화
    5. 최적화 결과의 마지막 장소를 목적지로 설정
    6. 카카오모빌리티 다중 경유지 길찾기 호출
    7. 프론트 지도용 경로 응답 반환
    """
    try:
        places = get_route_places(
            db=db,
            place_ids=request.place_ids,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    route_places: list[RoutePlace] = []

    for place in places:
        if place.latitude is None or place.longitude is None:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "좌표 정보가 없는 장소가 포함되어 있습니다.",
                    "place_id": place.id,
                    "place_name": place.title,
                },
            )

        route_places.append(
            RoutePlace(
                place_id=place.id,
                name=place.title,
                latitude=place.latitude,
                longitude=place.longitude,
            )
        )

    route_request = MultiRouteRequest(
        places=route_places,
        priority="RECOMMEND",
    )

    return await get_multi_directions(route_request)