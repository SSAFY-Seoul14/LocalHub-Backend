# app/services/chat_service.py
import os
from openai import OpenAI
from app.schemas.chat import MessageSchema
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

# 개발 모드 플래그 (True면 요금 차단 및 안전 개발 모드 작동)
DEV_MODE = os.getenv("DEV_MODE", "True").lower() == "true"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_ai_response(
    history: List[MessageSchema], 
    category: Optional[str] = None,
    seoul_realtime_data: Optional[str] = None
) -> str:
    """
    실시간 데이터를 기반으로 AI 답변을 생성합니다.
    DEV_MODE=True일 때는 요금을 한 푼도 쓰지 않는 정교한 시뮬레이션 답변이 나갑니다.
    """
    real_data = seoul_realtime_data or "현재 조회 가능한 구체적인 실시간 정보가 없습니다."

    # 1. 🛡️ 요금 절대 보존 모드 (DEV_MODE=True)
    if DEV_MODE:
        # 실제 AI가 대답하는 톤앤매너로 답변을 자연스럽게 흉내냅니다.
        simulated_answer = (
            f"안녕하세요! 서울을 가장 트렌디하게 소개해 드리는 'LocalHub AI 가이드'입니다. 🗺️✨\n\n"
            f"요청하신 정보를 바탕으로 실시간 서울 핫플레이스 목록을 가져왔어요. "
            f"오늘 가보시기 딱 좋은 코스로 추천해 드립니다!\n\n"
            f"📌 **실시간 추천 명소 목록**\n"
            f"{real_data}\n\n"
            f"선택하신 명소 주변의 맛집이나 이동 동선이 필요하시다면 언제든 편하게 질문해 주세요! "
            f"최고의 서울 여행 일정을 만들어 드릴게요. 🚗💨"
        )
        return simulated_answer

    # 2. 🚀 진짜 서비스 출시 & 최종 제출 모드 (DEV_MODE=False)
    # 2. 🚀 진짜 서비스 출시 & 최종 제출 모드 (DEV_MODE=False)
    system_guide = (
        "## [가이드 지침]\n"
        "너는 서울을 방문한 여행객을 위한 전문 가이드 'LocalHub AI'야.\n"
        "아래 제공되는 [실시간 서울 데이터]의 장소들을 절대적으로 최우선해서 답변을 작성해야 해.\n"
        "데이터에 없는 일반적인 유명 관광지(명동, 홍대, 강남 등)를 나열하느라 답변을 길게 쓰지 마.\n\n"
        
        "## [답변 작성 규칙]\n"
        "1. 질문과 매칭되는 [실시간 서울 데이터]의 장소들을 본문에 자연스럽게 녹여서 소개해 줘.\n"
        "2. 각 장소의 매력이나 유용한 팁을 1~2줄씩 친절한 어조로 붙여줘.\n"
        "3. 친절하고 정중한 존댓말(~해요, ~추천해 드려요)을 사용해 줘.\n"
        "4. 마크다운 가독성을 살리되, 전체 답변은 3~4문단 이내로 핵심만 깔끔하게 작성해 줘. (중언부언 금지)\n\n"
        
        f"## [실시간 서울 데이터]\n{real_data}\n\n"
        "## [사용자 질문]\n"
    )

    messages = []
    first_user_processed = False
    for msg in history:
        if msg.role == "user" and not first_user_processed:
            messages.append({"role": "user", "content": f"{system_guide}{msg.content}"})
            first_user_processed = True
        else:
            messages.append({"role": msg.role, "content": msg.content})

    if not messages:
        messages.append({"role": "user", "content": f"{system_guide}서울에 대해 소개해줘."})

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages     
        )
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"[ERROR] OpenAI API Call Failed: {str(e)}")
        # API 오류 시 대체 응답
        return (
            f"안녕하세요! 서울 AI 가이드입니다. 현재 서비스 호출량이 많아 기본 추천 목록을 전달해 드릴게요:\n\n"
            f"{real_data}\n\n이용에 불편을 드려 죄송합니다!"
        )