# FIRSTPARTY
from app.clients.models import Clients
from app.dao.base import BaseDao


class ClientsDAO(BaseDao):
    model = Clients
