# FIRSTPARTY
from app.dao.base import BaseDao
from app.operators.models import Operators


class OperatorsDAO(BaseDao):
    model = Operators
