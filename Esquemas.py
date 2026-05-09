from pydantic import BaseModel, Field
from typing import List, Literal, Optional

# class QueryResult(BaseModel):
#     columns: list[str]
#     rows: list[list[any]]
#     row_count: int
#     execution_time_ms: float
#     query_type: str
#     message: Optional[str] = None


# Esquemas para Frontend
#----------------------------------
class MessagePart(BaseModel):
    type: str  
    text: Optional[str] = None


class Message(BaseModel):
    id: str
    role: str 
    parts: List[MessagePart]

class ChatPayload(BaseModel):
    id: str
    messages: List[Message]
    trigger: str
#------------------------------------


#Esquemas AI component
#-----------------------------------
class SessionItem(BaseModel):
    day: str
    task: str
    duration_min: int

class WeekPlan(BaseModel):
    week: int
    sessions: List[SessionItem]


class Milestone(BaseModel):
    week: int
    target: str


class RiskItem(BaseModel):
    risk: str
    mitigation: str

class CoachResponse(BaseModel):
    response_type: Literal["plan", "answer", "fallback"]
    message_for_user: str
    plan_title: Optional[str] = None
    summary: str
    milestones: List[Milestone] = Field(default_factory=list)
    weekly_schedule: List[WeekPlan] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    next_actions: List[str] = Field(default_factory=list)


class ChatPayload(BaseModel):
    id: str
    messages: List[Message]
    trigger: str
    user_name: Optional[str] = None
    age: Optional[int] = None
    token: Optional[str] = None
    ai_settings: Optional[dict] = None
#-----------------------------------