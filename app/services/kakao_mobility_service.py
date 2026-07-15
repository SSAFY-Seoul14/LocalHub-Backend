from typing import Any

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.map import (
    MultiRouteRequest,
    MultiRouteResponse,
    OrderedRoutePlace,
    RouteCoordinate,
    RouteLeg,
    RouteLegPlace,
    RoutePlace,
    RouteResponse,
    RouteSummary,
)
from app.services.route_optimizer import optimize_route_order


KAKAO_DIRECTIONS_URL = (
    "https://apis-navi.kakaomobility.com/v1/directions"
)

KAKAO_WAYPOINTS_DIRECTIONS_URL = (
    "https://apis-navi.kakaomobility.com/v1/waypoints/directions"
)


async def get_directions(
    origin_longitude: float,
    origin_latitude: float,
    destination_longitude: float,
    destination_latitude: float,
    priority: str = "RECOMMEND",
) -> dict[str, Any]:
    """
    출발지와 목적지 사이의 자동차 길찾기 경로를 조회합니다.

    카카오 API 좌표 형식:
    경도(longitude),위도(latitude)
    """

    if not settings.KAKAO_REST_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="KAKAO_REST_API_KEY가 설정되지 않았습니다.",
        )

    headers = {
        "Authorization": (
            f"KakaoAK {settings.KAKAO_REST_API_KEY}"
        ),
    }

    params = {
        "origin": (
            f"{origin_longitude},{origin_latitude}"
        ),
        "destination": (
            f"{destination_longitude},{destination_latitude}"
        ),
        "priority": priority,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                KAKAO_DIRECTIONS_URL,
                headers=headers,
                params=params,
            )

        response.raise_for_status()

    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="카카오 길찾기 API 응답 시간이 초과되었습니다.",
        ) from exc

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "카카오 길찾기 API 호출에 실패했습니다.",
                "status_code": exc.response.status_code,
                "response": exc.response.text,
            },
        ) from exc

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="카카오 길찾기 API에 연결할 수 없습니다.",
        ) from exc

    data = response.json()

    return convert_kakao_route_response(data)


def convert_kakao_route_response(
    data: dict[str, Any],
) -> RouteResponse:
    """
    카카오 길찾기 원본 응답을 프론트용 RouteResponse로 변환합니다.
    """

    routes = data.get("routes", [])

    if not routes:
        raise HTTPException(
            status_code=404,
            detail="카카오 길찾기 결과가 없습니다.",
        )

    route = routes[0]

    if route.get("result_code") != 0:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "경로를 찾을 수 없습니다.",
                "result_code": route.get("result_code"),
                "result_msg": route.get("result_msg"),
            },
        )

    summary = route.get("summary", {})
    fare = summary.get("fare", {})

    origin_data = summary.get("origin", {})
    destination_data = summary.get("destination", {})

    path: list[RouteCoordinate] = []

    for section in route.get("sections", []):
        for road in section.get("roads", []):
            vertexes = road.get("vertexes", [])

            # vertexes 형식:
            # [경도1, 위도1, 경도2, 위도2, ...]
            for index in range(0, len(vertexes), 2):
                if index + 1 >= len(vertexes):
                    break

                longitude = vertexes[index]
                latitude = vertexes[index + 1]

                coordinate = RouteCoordinate(
                    latitude=latitude,
                    longitude=longitude,
                )

                # 도로 구간 연결 지점의 중복 좌표 제거
                if path and path[-1] == coordinate:
                    continue

                path.append(coordinate)

    if not path:
        raise HTTPException(
            status_code=404,
            detail="지도에 표시할 경로 좌표가 없습니다.",
        )

    return RouteResponse(
        distance=summary.get("distance", 0),
        duration=summary.get("duration", 0),
        taxi_fare=fare.get("taxi", 0),
        toll_fare=fare.get("toll", 0),
        origin=RouteCoordinate(
            latitude=origin_data.get("y"),
            longitude=origin_data.get("x"),
        ),
        destination=RouteCoordinate(
            latitude=destination_data.get("y"),
            longitude=destination_data.get("x"),
        ),
        path=path,
    )

async def get_multi_directions(
    request: MultiRouteRequest,
) -> MultiRouteResponse:
    if not settings.KAKAO_REST_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="KAKAO_REST_API_KEY가 설정되지 않았습니다.",
        )

    places = optimize_route_order(request.places)

    origin = places[0]
    destination = places[-1]
    waypoints = places[1:-1]

    headers = {
        "Authorization": (
            f"KakaoAK {settings.KAKAO_REST_API_KEY}"
        ),
        "Content-Type": "application/json",
    }

    body = {
        "origin": {
            "name": origin.name,
            "x": origin.longitude,
            "y": origin.latitude,
        },
        "destination": {
            "name": destination.name,
            "x": destination.longitude,
            "y": destination.latitude,
        },
        "waypoints": [
            {
                "name": waypoint.name,
                "x": waypoint.longitude,
                "y": waypoint.latitude,
            }
            for waypoint in waypoints
        ],
        "priority": request.priority,
        "alternatives": False,
        "road_details": False,
        "summary": False,
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                KAKAO_WAYPOINTS_DIRECTIONS_URL,
                headers=headers,
                json=body,
            )

        response.raise_for_status()

    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="카카오 다중 경유지 API 응답 시간이 초과되었습니다.",
        ) from exc

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "카카오 다중 경유지 API 호출에 실패했습니다.",
                "status_code": exc.response.status_code,
                "response": exc.response.text,
            },
        ) from exc

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="카카오 모빌리티 API에 연결할 수 없습니다.",
        ) from exc

    data = response.json()

    routes = data.get("routes", [])

    if not routes:
        raise HTTPException(
            status_code=404,
            detail="카카오 길찾기 결과가 없습니다.",
        )

    route = routes[0]

    if route.get("result_code") != 0:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "경로를 찾을 수 없습니다.",
                "result_code": route.get("result_code"),
                "result_msg": route.get("result_msg"),
            },
        )

    summary_data = route.get("summary", {})
    fare_data = summary_data.get("fare", {})

    ordered_places = create_ordered_places(places)
    legs = create_route_legs(route, places)
    full_path = create_full_path(legs)

    return MultiRouteResponse(
        optimized=True,
        summary=RouteSummary(
            distance=summary_data.get("distance", 0),
            duration=summary_data.get("duration", 0),
            taxi_fare=fare_data.get("taxi", 0),
            toll_fare=fare_data.get("toll", 0),
        ),
        places=ordered_places,
        legs=legs,
        full_path=full_path,
    )

def create_ordered_places(
    places: list,
) -> list[OrderedRoutePlace]:
    ordered_places: list[OrderedRoutePlace] = []

    last_index = len(places) - 1

    for index, place in enumerate(places):
        if index == 0:
            role = "ORIGIN"
        elif index == last_index:
            role = "DESTINATION"
        else:
            role = "WAYPOINT"

        ordered_places.append(
            OrderedRoutePlace(
                order=index + 1,
                role=role,
                place_id=place.place_id,
                name=place.name,
                latitude=place.latitude,
                longitude=place.longitude,
            )
        )

    return ordered_places


def extract_path_from_roads(
    roads: list[dict],
) -> list[RouteCoordinate]:
    path: list[RouteCoordinate] = []

    for road in roads:
        vertexes = road.get("vertexes", [])

        for index in range(0, len(vertexes), 2):
            if index + 1 >= len(vertexes):
                break

            coordinate = RouteCoordinate(
                longitude=vertexes[index],
                latitude=vertexes[index + 1],
            )

            if path and path[-1] == coordinate:
                continue

            path.append(coordinate)

    return path


def convert_to_leg_place(
    place: RoutePlace,
) -> RouteLegPlace:
    return RouteLegPlace(
        place_id=place.place_id,
        name=place.name,
        latitude=place.latitude,
        longitude=place.longitude,
    )


def create_route_legs(
    route: dict,
    places: list[RoutePlace],
) -> list[RouteLeg]:
    sections = route.get("sections", [])
    expected_section_count = len(places) - 1

    if len(sections) != expected_section_count:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "카카오 경로 구간 수와 장소 수가 일치하지 않습니다.",
                "place_count": len(places),
                "section_count": len(sections),
            },
        )

    legs: list[RouteLeg] = []

    for index, section in enumerate(sections):
        section_path = extract_path_from_roads(
            section.get("roads", [])
        )

        legs.append(
            RouteLeg(
                order=index + 1,
                origin=convert_to_leg_place(places[index]),
                destination=convert_to_leg_place(
                    places[index + 1]
                ),
                distance=section.get("distance", 0),
                duration=section.get("duration", 0),
                path=section_path,
            )
        )

    return legs


def create_full_path(
    legs: list[RouteLeg],
) -> list[RouteCoordinate]:
    full_path: list[RouteCoordinate] = []

    for leg in legs:
        for coordinate in leg.path:
            if full_path and full_path[-1] == coordinate:
                continue

            full_path.append(coordinate)

    return full_path