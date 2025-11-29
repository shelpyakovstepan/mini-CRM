# THIRDPARTY
from pydantic import BaseModel


class SClients(BaseModel):
    id: int
    email: str
