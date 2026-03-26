from pydantic import BaseModel, Field
from typing import Optional, Any, Dict

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
    origin: Optional[str] = "chat"
    incident_source: Optional[str] = None

class ErrorMessage(BaseMessage):
    pass

class QuestionMessage(BaseMessage):
    pass

class SavePropertyRequest(BaseModel):
    description: str
    protocol: list[str]
    name: str
    content: str

class SendToMonitoringRequest(BaseModel):
    name: Optional[str] = None
    content: str

class ReceivedEventRequest(BaseModel):
    source: Optional[str] = Field(default=None, description="Source of the event")
    event: Dict[str, Any] = Field(..., description="MISP-like event payload")

class ReceivedEventResponse(BaseModel):
    message: str
    source: Optional[str] = None