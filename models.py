from pydantic import BaseModel


class KeyResponse(BaseModel):
    key: str


class UserIdResponse(BaseModel):
    id: int
