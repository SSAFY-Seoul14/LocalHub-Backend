from sqlalchemy.orm import Session

from app.models.place import Place

def find_places_by_ids(
    db: Session,
    place_ids: list[int],
) -> list[Place]:
    """
    여러 장소 ID를 한 번에 조회하고,
    요청받은 place_ids 순서대로 반환합니다.
    """

    places = (
        db.query(Place)
        .filter(Place.id.in_(place_ids))
        .all()
    )

    place_by_id = {
        place.id: place
        for place in places
    }

    return [
        place_by_id[place_id]
        for place_id in place_ids
        if place_id in place_by_id
    ]