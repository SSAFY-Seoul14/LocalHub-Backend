from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.place import Place


def get_route_places(
    db: Session,
    place_ids: list[int],
) -> list[Place]:
    """
    경로 생성 요청에 포함된 장소들을 데이터베이스에서 조회한다.

    요청으로 전달된 place_ids의 순서를 유지하여 장소 목록을 반환한다.

    Args:
        db: SQLAlchemy 데이터베이스 세션.
        place_ids: 경로에 포함할 장소 ID 목록.

    Returns:
        요청 순서대로 정렬된 장소 목록.

    Raises:
        ValueError: 중복된 장소 ID가 포함된 경우.
        ValueError: 존재하지 않는 장소 ID가 포함된 경우.
        ValueError: 위도 또는 경도가 없는 장소가 포함된 경우.
    """

    if len(place_ids) != len(set(place_ids)):
        raise ValueError(
            "중복된 장소 ID가 포함되어 있습니다."
        )

    statement = select(Place).where(
        Place.id.in_(place_ids)
    )

    places = list(
        db.scalars(statement).all()
    )

    place_by_id = {
        place.id: place
        for place in places
    }

    missing_place_ids = [
        place_id
        for place_id in place_ids
        if place_id not in place_by_id
    ]

    if missing_place_ids:
        raise ValueError(
            f"존재하지 않는 장소 ID가 포함되어 있습니다: "
            f"{missing_place_ids}"
        )

    ordered_places = [
        place_by_id[place_id]
        for place_id in place_ids
    ]

    invalid_coordinate_place_ids = [
        place.id
        for place in ordered_places
        if place.latitude is None
        or place.longitude is None
    ]

    if invalid_coordinate_place_ids:
        raise ValueError(
            f"위치 정보가 없는 장소가 포함되어 있습니다: "
            f"{invalid_coordinate_place_ids}"
        )

    return ordered_places