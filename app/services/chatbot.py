from app.schemas.chatbot import ChatRequest

# TODO: 실제 데이터로 변경
MOCK_SEOUL_DATA = {
    "관광지": [
        {"title": "경복궁", "address": "종로구 사직로 161", "description": "조선 시대의 법궁으로 서울의 대표적인 역사 관광지입니다."},
        {"title": "N서울타워", "address": "용산구 남산공원길 105", "description": "서울의 야경을 한눈에 볼 수 있는 랜드마크입니다."}
    ],
    "축제공연": [
        {"title": "서울세계불꽃축제", "address": "여의도 한강공원", "description": "매년 10월에 열리는 환상적인 불꽃쇼 축제입니다."},
        {"title": "한강 달빛 야시장", "address": "반포 한강공원", "description": "푸드트럭 and 플리마켓이 열리는 서울의 밤 대표 행사입니다."}
    ],
    "숙박": [
        {"title": "시그니엘 서울", "address": "송파구 올림픽로 300", "description": "롯데월드타워에 위치한 초호화 최고급 호텔입니다."}
    ]
}

class ChatBotService:
    @staticmethod
    def generate_mock_response(request_data: ChatRequest) -> str:
        # 1. FE가 보낸 마지막 질문 추출
        user_message = request_data.history[-1].content
        
        # 2. 아주 간단한 키워드 탐색 매칭 (가짜 검색 엔진)
        found_info = []
        for category, items in MOCK_SEOUL_DATA.items():
            for item in items:
                # 사용자의 질문에 타이틀이나 카테고리명이 포함되어 있다면 해당 데이터를 가져옴
                if item["title"] in user_message or category in user_message or "서울" in user_message:
                    found_info.append(f"[{category}] {item['title']} ({item['address']}) - {item['description']}")

        # 3. 매칭된 데이터가 있다면 묶어서 답변 스케치, 없으면 기본 답변
        if found_info:
            context = "\n".join(found_info[:2]) # 상위 2개만 추출
            return f"🤖 [LocalHub AI Mock 가이드]\n요청하신 정보와 관련된 서울 공공데이터를 찾았습니다:\n\n{context}\n\n(※ 현재 백엔드가 Mock 데이터 모드로 작동 중이며, 정식 연동 시 OpenAI가 훨씬 자연스럽게 가공해 줍니다!)"
        
        return f"🤖 [LocalHub AI Mock 가이드]\n질문하신 '{user_message}'에 대한 데이터를 찾지 못했습니다. '관광지', '축제공연', '숙박' 키워드를 포함해서 질문해 보세요!"