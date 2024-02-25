from pydantic import BaseModel, EmailStr


class User(BaseModel):
    login: str


class ExternalUser(User):
    mail: EmailStr
