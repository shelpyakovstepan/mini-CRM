# STDLIB
from typing import List

# THIRDPARTY
from fastapi import APIRouter

# FIRSTPARTY
from app.clients.dao import ClientsDAO
from app.clients.schemas import SClients
from app.database import DbSession

router = APIRouter(
    prefix="/clients",
    tags=["Клиенты/Лиды"],
)


@router.get("/all")
async def get_all_clients(session: DbSession) -> List[SClients]:
    all_clients = await ClientsDAO.find_all(session=session)
    return all_clients
