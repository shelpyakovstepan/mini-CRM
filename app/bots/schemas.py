# THIRDPARTY
from pydantic import BaseModel


class SBots(BaseModel):
    id: int
    operators: dict
