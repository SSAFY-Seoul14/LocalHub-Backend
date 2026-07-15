from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.db.database import Base 

class ChatHistory(Base):
    """
    사용자와 AI 가이드의 대화 내역을 누적하여 저장하는 테이블 모델
    """
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 추후 세션별/유저별 대화를 구분하기 위해 session_id를 남겨둠. (기본값은 'default')
    session_id = Column(String(50), default="default", index=True)
    # 'user' 또는 'assistant'
    role = Column(String(20), nullable=False)
    # 실제 대화 텍스트 내용
    content = Column(Text, nullable=False)
    # 어떤 카테고리(예: 'accommodation', 'attraction' 등)로 처리되었는지 기록 (비어있을 수 있음)
    category = Column(String(50), nullable=True)
    # 대화가 일어난 시간
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))