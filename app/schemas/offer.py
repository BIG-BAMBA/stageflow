from pydantic import BaseModel, Field


class OfferCreate(BaseModel):
    title: str = Field(min_length=1)
    mission: str = Field(min_length=1)
    competences: str = Field(min_length=1)
    company_id: int | None = None


class OfferRead(BaseModel):
    id: int
    title: str
    mission: str
    competences: str
    company_id: int
    status: str


class OfferReview(BaseModel):
    decision: str
