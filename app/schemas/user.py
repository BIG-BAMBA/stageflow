from pydantic import BaseModel, EmailStr


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
