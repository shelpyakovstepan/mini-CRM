# THIRDPARTY
from pydantic import BaseModel


class SOperators(BaseModel):
    id: int
    status: int
    limit_of_contacts: int
