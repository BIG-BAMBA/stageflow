from pydantic import BaseModel


class ApplicationRead(BaseModel):
    id: int
    student_id: int
    offer_id: int
    status: str


class ApplicationDecision(BaseModel):
    decision: str
