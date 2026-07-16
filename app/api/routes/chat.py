from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chatplace_service import fetch_seoul_places
from app.services.chat_service import generate_ai_response
from typing import Optional, Tuple

router = APIRouter()

# 서울시 25개 자치구 목록
SEOUL_GU_LIST = [
    "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구",
    "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구",
    "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"
]

CATEGORY_KEYWORDS = {
    "tourism": ["관광지", "관광", "명소", "가볼만한곳", "핫플", "가볼 만한 곳", "공원", "한강", "야경", "전망대"],
    "activity": ["레포츠", "액티비티", "스포츠", "자전거", "수상스키", "클라이밍", "하이킹", "등산", "체험"],
    "culture": ["문화시설", "미술관", "박물관", "전시회", "전시", "갤러리", "문화", "역사관", "도서관"],
    "shopping": ["쇼핑", "시장", "백화점", "아울렛", "면세점", "상점가", "소품샵", "마트"],
    "accommodation": ["숙박", "숙소", "호텔", "게스트하우스", "펜션", "민박", "모텔", "호스텔"],
    "itinerary": ["여행코스", "코스", "추천코스", "일정", "루트", "당일치기", "1박2일", "여행 경로"],
    "event": ["축제공연", "축제", "공연", "콘서트", "행사", "이벤트", "연극", "뮤지컬", "페스티벌"]
}


# 일상 인사말/잡담으로 판단할 키워드 정의
INTRO_KEYWORDS = ["안녕", "반가워", "누구", "하이", "기분", "이름", "소개", "고마워", "감사", "ok"]

def analyze_user_intent(text: str, history: list) -> Tuple[Optional[str], Optional[str]]:
    """
    유저의 발화와 이전 대화 흐름을 종합하여 (카테고리, 자치구)를 동적으로 추론합니다.
    단, 명확한 일상 인사/잡담일 때는 맥락 상속을 차단합니다.
    """
    cleaned_text = text.replace(" ", "").lower()
    
    # 질문 자체가 단순 일상 인사나 잡담 키워드를 포함하고 있다면
    # 이전 맥락(관광, 쇼핑 등)을 상속받지 않고 즉시 (None, None)을 리턴하여 API 조회를 방지합니다.
    if any(intro in cleaned_text for intro in INTRO_KEYWORDS):
        print("[DEBUG] Intro/General greeting detected. Blocking context inheritance.")
        return None, None

    # 1. 자치구(Gu) 추출
    detected_gu = None
    for gu in SEOUL_GU_LIST:
        if gu in text or gu[:-1] in text:
            detected_gu = gu
            break
            
    # 2. 카테고리 추출
    detected_category = None
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            cleaned_keyword = keyword.replace(" ", "")
            if cleaned_keyword in cleaned_text:
                detected_category = category
                break
        if detected_category:
            break
            
    # 3. 맥락 상속 (이전 질문이 일반 인사/잡담이 아닐 때만 안전하게 동작)
    if not detected_category and history:
        for msg in reversed(history[:-1]):
            if msg.role == "user" and getattr(msg, "category", None):
                detected_category = msg.category
                break
            for category, keywords in CATEGORY_KEYWORDS.items():
                for keyword in keywords:
                    if keyword.replace(" ", "") in msg.content.replace(" ", ""):
                        detected_category = category
                        break
                if detected_category:
                    break

    return detected_category, detected_gu


@router.post("/api/chat", response_model=ChatResponse, summary="LocalHub AI 가이드 질의응답")
async def chat_endpoint(payload: ChatRequest):
    try:
        user_message = payload.history[-1].content if payload.history else ""
        category = payload.category

        # 1. 질문 분석기 가동 (카테고리와 '구' 정보 동시 추출)
        auto_category, detected_gu = analyze_user_intent(user_message, payload.history)
        
        # 프론트가 칩을 직접 눌렀거나, 분석기가 찾은 카테고리 우선 선택
        final_category = category or auto_category
        
        print(f"[DEBUG] Final Category: {final_category} | Detected Gu: {detected_gu}")

        # 2. 필터링된 실시간 데이터 가져오기
        seoul_realtime_data = None
        if final_category:
            # fetch_seoul_places에 구(gu) 정보도 함께 넘기기
            seoul_realtime_data = await fetch_seoul_places(category=final_category, query=detected_gu)
            print(f"[DEBUG] Realtime Data Fetched (Gu={detected_gu}):\n{seoul_realtime_data}")
        else:
            print("[DEBUG] No category detected. General Chat.")

        # 3. GPT 응답 생성
        ai_answer = generate_ai_response(payload.history, final_category, seoul_realtime_data)

        # 프론트에 넘겨줄 때 응답 데이터 구조 생성
        return ChatResponse(
            answer=ai_answer,
            success=True
        )

    except Exception as e:
        print(f"[ERROR] Chat Endpoint Error: {str(e)}")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")