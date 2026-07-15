from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.place import (
    PlaceDetailResponse,
    PlaceListResponse,
)

from app.services.place_service import (
    get_place_by_id,
    get_places,
    get_places_in_bounds,
)

router = APIRouter(
    prefix="/api/places",
    tags=["Places"],
)


@router.get(
    "",
    response_model=list[PlaceListResponse],
    summary="전체 장소 목록 조회",
)
def read_places(
    content_type: str | None = None,
    db: Session = Depends(get_db),
) -> list[PlaceListResponse]:
    """
    지도에 표시할 장소 목록을 조회한다.

    content_type을 전달하면 해당 유형만 조회한다.
    """

    return get_places(
        db=db,
        content_type=content_type,
    )

@router.get(
    "/map",
    response_model=list[PlaceListResponse],
    summary="지도 화면 범위 내 장소 조회",
)
def read_places_in_bounds(
    min_lat: float = Query(
        ...,
        ge=-90,
        le=90,
        description="지도 남쪽 경계 위도",
    ),
    max_lat: float = Query(
        ...,
        ge=-90,
        le=90,
        description="지도 북쪽 경계 위도",
    ),
    min_lng: float = Query(
        ...,
        ge=-180,
        le=180,
        description="지도 서쪽 경계 경도",
    ),
    max_lng: float = Query(
        ...,
        ge=-180,
        le=180,
        description="지도 동쪽 경계 경도",
    ),
    content_type: str | None = Query(
        default=None,
        description="관광지, 음식점, 숙박 등 콘텐츠 유형",
    ),
    limit: int = Query(
        default=1000,
        ge=1,
        le=3000,
        description="최대 조회 개수",
    ),
    db: Session = Depends(get_db),
) -> list[PlaceListResponse]:
    """
    현재 지도에 보이는 범위의 장소만 조회한다.
    """

    if min_lat > max_lat:
        raise HTTPException(
            status_code=400,
            detail="min_lat은 max_lat보다 작아야 합니다.",
        )

    if min_lng > max_lng:
        raise HTTPException(
            status_code=400,
            detail="min_lng은 max_lng보다 작아야 합니다.",
        )

    return get_places_in_bounds(
        db=db,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lng=min_lng,
        max_lng=max_lng,
        content_type=content_type,
        limit=limit,
    )

@router.get(
    "/{place_id}",
    response_model=PlaceDetailResponse,
    summary="장소 상세 조회",
)
def read_place(
    place_id: int,
    db: Session = Depends(get_db),
) -> PlaceDetailResponse:
    """
    장소 상세 정보를 조회한다.
    """

    place = get_place_by_id(
        place_id=place_id,
        db=db,
    )

    if place is None:
        raise HTTPException(
            status_code=404,
            detail="장소를 찾을 수 없습니다.",
        )

    return place