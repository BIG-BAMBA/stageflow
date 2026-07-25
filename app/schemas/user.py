from pydantic import BaseModel, EmailStr, Field


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str


class UserMe(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str


class UserRoleUpdate(BaseModel):
    role: str = Field(..., examples=["student", "company", "program_manager", "admin"])
