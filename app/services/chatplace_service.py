import httpx
from typing import List, Dict, Any, Optional
import random

PLACE_API_URL = "https://localhub-backend-hwr2.onrender.com/api/places"

# 챗봇 영문 카테고리 -> 한글 content_type으로 변환
CATEGORY_TO_CONTENT_TYPE = {
    "tourism": "관광지",
    "activity": "레포츠",
    "culture": "문화시설",
    "shopping": "쇼핑",
    "accommodation": "숙박",
    "itinerary": "여행코스",
    "event": "축제공연"
}

async def fetch_seoul_places(category: Optional[str] = None) -> str:
    """
    장소 API를 비동기(HTTPX)로 호출하여 데이터를 받아옵니다.
    """
    # 만약 카테고리가 감지되지 않았다면, 기본값으로 '관광지' 데이터를 조회하게 유도
    content_type = CATEGORY_TO_CONTENT_TYPE.get(category) if category else "관광지"
    
    params = {}
    if content_type:
        params["content_type"] = content_type

    print(f"[DEBUG] Fetching places from Place API with parameters: {params}")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(PLACE_API_URL, params=params)
            
            if response.status_code == 200:
                data = response.json()
                # 실제 넘어오는 데이터 형식에 맞춰 포맷팅 함수 호출
                return format_places_data(data)
            else:
                print(f"[WARNING] Place API returned status code {response.status_code}")
                return "실시간 서울 지역 정보를 일시적으로 불러올 수 없습니다."
                
    except Exception as e:
        print(f"[ERROR] Failed to fetch data from Place API: {str(e)}")
        return "현재 실시간 서울 정보를 조회할 수 없습니다."


def format_places_data(places_list: List[Dict[str, Any]]) -> str:
    """
    실제 장소 API 응답 필드 구조(title, content_type 등)에 완벽히 호환되도록 문자열로 가공
    """
    if not places_list:
        return "조회된 실시간 서울 지역 정보가 없습니다."
        
    formatted_items = []


    # api 응답 리스트 중 랜덤으로 3개 추출
    sample_size = min(len(places_list), 3)
    random_places = random.sample(places_list, sample_size)
    
    for place in random_places:
        title = place.get("title", "정보 없음")
        content_type = place.get("content_type", "추천 정보")
        
        # 실제 넘어오는 데이터에 주소 정보가 없다면 생략하거나 이름 위주로 전달.
        formatted_items.append(f"- [{content_type}] {title}")
        
    return "\n".join(formatted_items)