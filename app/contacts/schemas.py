# THIRDPARTY
from pydantic import BaseModel


class SContacts(BaseModel):
    id: int
    client_id: int
    bots_id: int
    operator_id: int
