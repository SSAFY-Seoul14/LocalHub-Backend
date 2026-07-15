from app.schemas.map import RoutePlace


RouteDurationMatrix = dict[int, dict[int, int]]


def calculate_total_duration(
    places: list[RoutePlace],
    duration_matrix: RouteDurationMatrix,
) -> int:
    """
    주어진 방문 순서의 전체 예상 이동시간을 계산합니다.

    반환 단위:
    초
    """

    total_duration = 0

    for index in range(len(places) - 1):
        origin = places[index]
        destination = places[index + 1]

        total_duration += duration_matrix[
            origin.place_id
        ][destination.place_id]

    return total_duration


def optimize_route_order(
    places: list[RoutePlace],
    duration_matrix: RouteDurationMatrix,
) -> list[RoutePlace]:
    """
    첫 번째 장소만 출발지로 고정하고,
    나머지 모든 장소를 카카오 자동차 예상 소요시간 기준으로
    최근접 이웃 방식으로 정렬합니다.

    최적화 결과의 마지막 장소가 자동 목적지가 됩니다.
    """

    if len(places) <= 2:
        return places

    origin = places[0]
    unvisited = places[1:].copy()

    optimized_places: list[RoutePlace] = [origin]
    current_place = origin

    while unvisited:
        nearest_place = min(
            unvisited,
            key=lambda place: duration_matrix[
                current_place.place_id
            ][place.place_id],
        )

        optimized_places.append(nearest_place)
        unvisited.remove(nearest_place)
        current_place = nearest_place

    return optimized_places