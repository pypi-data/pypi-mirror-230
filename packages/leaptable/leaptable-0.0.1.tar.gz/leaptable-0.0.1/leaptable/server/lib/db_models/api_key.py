from pydantic import BaseModel


class ApiKey(BaseModel):
    description: str
