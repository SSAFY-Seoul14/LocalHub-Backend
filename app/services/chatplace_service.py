import httpx
from typing import List, Dict, Any, Optional
import random

PLACE_API_URL = "https://localhub-backend-hwr2.onrender.com/api/places"

CATEGORY_TO_CONTENT_TYPE = {
    "tourism": "관광지",
    "activity": "레포츠",
    "culture": "문화시설",
    "shopping": "쇼핑",
    "accommodation": "숙박",
    "itinerary": "여행코스",
    "event": "축제공연행사"
}

async def fetch_seoul_places(category: Optional[str] = None, query: Optional[str] = None) -> str:
    """
    장소 API를 비동기로 호출하고, 특정 '구(Gu)'가 지정된 경우 
    백엔드 단에서 주소(address) 정보를 기반으로 수동 필터링합니다.
    """
    if not category:
        return "조회된 실시간 서울 지역 정보가 없습니다."
        
    content_type = CATEGORY_TO_CONTENT_TYPE.get(category)
    if not content_type:
        return "조회된 실시간 서울 지역 정보가 없습니다."
    
    # 장소 조회 API에는 content_type(카테고리)만 파라미터로 보냄.
    params = {"content_type": content_type}
    print(f"[DEBUG] Fetching raw places from API for category: {content_type}")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(PLACE_API_URL, params=params)
            
            if response.status_code == 200:
                places_list = response.json() # 전체 장소 리스트 받아오기
                
                # 구역별 필터링
                if query and isinstance(places_list, list):
                    # 주소(address)나 상세주소(address_detail), 제목(title)에 "광진구" 등이 포함된 것만 필터링
                    filtered_places = [
                        p for p in places_list 
                        if (
                            query in p.get("address", "") or 
                            query in p.get("address_detail", "") or 
                            query in p.get("title", "")
                        )
                    ]
                    print(f"[DEBUG] Sucessfully filtered with '{query}' on backend: {len(places_list)} -> {len(filtered_places)} items")
                    
                    # 만약 사용자가 말한 구에 해당하는 데이터가 우리 DB에 단 하나도 없다면,
                    # 아무것도 추천 안 해주는 것보다는 전체 리스트 중에서 보여주는 게 나으므로 원래 리스트 사용
                    if filtered_places:
                        places_list = filtered_places
                    else:
                        print(f"[DEBUG] No data matched for '{query}'. Using whole category list instead.")
                
                return format_places_data(places_list)
            else:
                print(f"[WARNING] Place API returned status code {response.status_code}")
                return "실시간 서울 지역 정보를 일시적으로 불러올 수 없습니다."
                
    except Exception as e:
        print(f"[ERROR] Failed to fetch data from Place API: {str(e)}")
        return "현재 실시간 서울 정보를 조회할 수 없습니다."


def format_places_data(places_list: List[Dict[str, Any]]) -> str:
    """
    실제 장소 API 응답 필드 구조에 맞게 문자열로 가공합니다.
    """
    if not places_list:
        return "조회된 실시간 서울 지역 정보가 없습니다."
        
    formatted_items = []

    # 필터링을 거치고 살아남은 결과 중 최대 3개만 무작위 추출
    sample_size = min(len(places_list), 3)
    random_places = random.sample(places_list, sample_size)
    
    for place in random_places:
        title = place.get("title", "정보 없음")
        content_type = place.get("content_type", "추천 정보")
        address = place.get("address", "").replace("서울특별시 ", "") # 가독성을 위해 '서울특별시' 생략
        content_id = place.get("contentid") or place.get("content_id") or place.get("contentId") or "0"
        # OpenAI가 자치구 정보를 확실하게 인지할 수 있도록 가공
        formatted_items.append(f"- [{content_type}] {title} (위치: {address}, contentId: {content_id})")
        
    return "\n".join(formatted_items)