from pydantic import BaseModel
from typing import List, Optional

# === Đặt tất cả Pydantic models của bạn vào đây ===

# Schemas cho Session
class SessionAnswerIn(BaseModel):
    question_id: int
    selected_option: str

class SaveAnswersPayload(BaseModel):
    answers: List[SessionAnswerIn]
