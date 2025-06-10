from pydantic import BaseModel
from typing import Optional

class PromptRequest(BaseModel):
    input_text: str
    protocol_list: list[str]

class BaseMessage(BaseModel):
    type: str
    role: str
    content: str

class PropertyMessage(BaseMessage):
    status: str
    editable: bool
    ask_to_save: bool
    validation_feedback: Optional[str] = None

class ErrorMessage(BaseMessage):
    pass

class QuestionMessage(BaseMessage):
    pass

class SavePropertyRequest(BaseModel):
    description: str
    protocol: list[str]
    name: str
    content: str