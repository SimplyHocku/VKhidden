from pydantic import BaseModel


class KeyResponse(BaseModel):
    key: str
    remember: bool = None


class UserIdResponse(BaseModel):
    id: int


class MsgForEncrypt(BaseModel):
    msg: str


class SecretKey(BaseModel):
    key_name: str


class Message(BaseModel):
    msg_text: str
    crypt: bool
    user_id: int

class GuestModel(BaseModel):
    guest_alias: str

class GuestDataModel(BaseModel):
    host: str
    alias: str
    allow: bool
