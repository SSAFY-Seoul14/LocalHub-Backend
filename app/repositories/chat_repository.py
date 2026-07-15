from sqlalchemy.orm import Session
from app.models.chat import ChatHistory
from app.schemas.chat import MessageSchema
from typing import List

class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_message(self, role: str, content: str, category: str = None, session_id: str = "default") -> ChatHistory:
        """
        한 건의 대화 메시지를 데이터베이스에 저장합니다.
        """
        db_chat = ChatHistory(
            session_id=session_id,
            role=role,
            content=content,
            category=category
        )
        self.db.add(db_chat)
        self.db.commit()
        self.db.refresh(db_chat)
        return db_chat

    def get_chat_history(self, session_id: str = "default", limit: int = 20) -> List[ChatHistory]:
        """
        최근 대화 이력을 가져옵니다. (기본 최근 20개)
        """
        return (
            self.db.query(ChatHistory)
            .filter(ChatHistory.session_id == session_id)
            .order_by(ChatHistory.created_at.asc())  # 시간 오름차순으로 정렬해서 순서대로 반환
            .limit(limit)
            .all()
        )