from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chatplace_service import fetch_seoul_places
from app.services.chat_service import generate_ai_response
from typing import Optional

router = APIRouter()

# 1. 룰 베이스 카테고리 분류용 키워드 사전 정의
# 키: 영문 카테고리명, 값: 분류에 매칭될 한글 키워드들
CATEGORY_KEYWORDS = {
    "tourism": ["관광지", "관광", "명소", "가볼만한곳", "핫플", "가볼 만한 곳", "공원", "한강", "야경", "전망대"],
    "activity": ["레포츠", "액티비티", "스포츠", "자전거", "수상스키", "클라이밍", "하이킹", "등산", "체험"],
    "culture": ["문화시설", "미술관", "박물관", "전시회", "전시", "갤러리", "문화", "역사관", "도서관"],
    "shopping": ["쇼핑", "시장", "백화점", "아울렛", "면세점", "상점가", "소품샵", "마트"],
    "accommodation": ["숙박", "숙소", "호텔", "게스트하우스", "펜션", "민박", "모텔", "호스텔"],
    "itinerary": ["여행코스", "코스", "추천코스", "일정", "루트", "당일치기", "1박2일", "여행 경로"],
    "event": ["축제공연", "축제", "공연", "콘서트", "행사", "이벤트", "연극", "뮤지컬", "페스티벌"]
}

def classify_category_from_text(text: str) -> Optional[str]:
    """
    유저의 자연어 질문에서 키워드를 파싱하여 영문 카테고리 식별자를 반환합니다.
    매치되는 키워드가 없으면 None을 반환합니다.
    """
    # 공백 제거 및 소문자 변환(혹시 모를 영어 입력 대비)
    cleaned_text = text.replace(" ", "").lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            # 띄어쓰기가 없어진 상태에서 키워드가 포함되어 있는지 매칭 검사
            cleaned_keyword = keyword.replace(" ", "")
            if cleaned_keyword in cleaned_text:
                return category
                
    return None  # 매치되는 카테고리가 없는 



@router.post("/chat", response_model=ChatResponse, summary="LocalHub AI 가이드 질의응답")
async def chat_endpoint(payload: ChatRequest):
    """
    사용자의 질문과 이전 대화 내역, 카테고리를 전달받아 분석 후 최적의 응답을 반환합니다.
    """
    try:
        # 프론트가 보낸 원본 값 확인 (디버깅)
        user_message = payload.history[-1].content if payload.history else ""
        category = payload.category

        print(f"[DEBUG] Client Sent Category: {category}")
        print(f"[DEBUG] Client Sent Message: '{user_message}'")

        # 2. 카테고리값이 들어오지 않은 경우 (자연어 직접 타이핑) 분기 처리
        if not category:
            # 자연어 분석기를 돌려서 카테고리 추론
            category = classify_category_from_text(user_message)
            print(f"[DEBUG] -> Categorized by Natural Language Parser: {category}")
        else:
            print(f"[DEBUG] -> Categorized directly by Quick Chip: {category}")

        # 2. [실제 연동] 비동기 함수로 배포된 서버에서 실시간 장소를 불러옴.
        seoul_realtime_data = await fetch_seoul_places(category)
        print(f"[DEBUG] Realtime Data Fetched:\n{seoul_realtime_data}")

        # 3. 수집한 실시간 데이터와 대화 맥락을 OpenAI GPT에 전달하여 답변 생성
        ai_answer = generate_ai_response(payload.history, category, seoul_realtime_data)

        return ChatResponse(
            answer=ai_answer,
            success=True
        )

        
        
    except Exception as e:
        print(f"[ERROR] Chat Endpoint Error: {str(e)}")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")