from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.place import Place


def get_places(
    db: Session,
    content_type: str | None = None,
) -> list[Place]:
    """
    장소 목록을 조회한다.
    """

    statement = select(Place)

    if content_type:
        statement = statement.where(
            Place.content_type == content_type
        )

    statement = statement.order_by(
        Place.title
    )

    return list(
        db.scalars(statement).all()
    )

def get_places_in_bounds(
    db: Session,
    *,
    min_lat: float,
    max_lat: float,
    min_lng: float,
    max_lng: float,
    content_type: str | None = None,
    limit: int = 1000,
) -> list[Place]:
    """
    현재 지도 화면 범위 안에 있는 장소를 조회한다.
    """

    statement = select(Place).where(
        Place.latitude.is_not(None),
        Place.longitude.is_not(None),
        Place.latitude >= min_lat,
        Place.latitude <= max_lat,
        Place.longitude >= min_lng,
        Place.longitude <= max_lng,
    )

    if content_type:
        statement = statement.where(
            Place.content_type == content_type
        )

    statement = (
        statement
        .order_by(Place.title)
        .limit(limit)
    )

    return list(
        db.scalars(statement).all()
    )


def get_place_by_id(
    place_id: int,
    db: Session,
) -> Place | None:
    """
    장소 상세 정보를 조회한다.
    """

    statement = (
        select(Place)
        .where(Place.id == place_id)
    )

    return db.scalar(statement)