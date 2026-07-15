from math import asin, cos, radians, sin, sqrt

from app.schemas.map import RoutePlace


def calculate_haversine_distance(
    first: RoutePlace,
    second: RoutePlace,
) -> float:
    """
    두 좌표 사이의 직선거리를 계산합니다.

    반환 단위:
    km
    """

    earth_radius_km = 6371.0

    latitude_difference = radians(
        second.latitude - first.latitude
    )
    longitude_difference = radians(
        second.longitude - first.longitude
    )

    first_latitude = radians(first.latitude)
    second_latitude = radians(second.latitude)

    value = (
        sin(latitude_difference / 2) ** 2
        + cos(first_latitude)
        * cos(second_latitude)
        * sin(longitude_difference / 2) ** 2
    )

    central_angle = 2 * asin(sqrt(value))

    return earth_radius_km * central_angle

def optimize_route_order(
    places: list[RoutePlace],
) -> list[RoutePlace]:
    """
    출발지와 목적지는 고정하고,
    중간 경유지만 최근접 이웃 방식으로 정렬합니다.
    """

    if len(places) <= 2:
        return places

    origin = places[0]
    destination = places[-1]

    unvisited = places[1:-1].copy()

    optimized_places: list[RoutePlace] = [origin]

    current_place = origin

    while unvisited:
        nearest_place = min(
            unvisited,
            key=lambda place: calculate_haversine_distance(
                current_place,
                place,
            ),
        )

        optimized_places.append(nearest_place)
        unvisited.remove(nearest_place)
        current_place = nearest_place

    optimized_places.append(destination)

    return optimized_places