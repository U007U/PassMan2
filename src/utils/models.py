from pydantic import BaseModel


class UserCredentials(BaseModel):
    service: str
    login: str
    password: str
