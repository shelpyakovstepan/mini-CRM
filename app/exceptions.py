# THIRDPARTY
from fastapi import HTTPException, status


class BaseAppException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class NotOperatorWithThisId(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Not operator with this ID"


class NotBotWithThisId(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Not bot with this ID"


class NotOperatorForYourContact(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Not operator for your contact"
