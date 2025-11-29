# STDLIB
from typing import List

# THIRDPARTY
from fastapi import APIRouter

# FIRSTPARTY
from app.bots.dao import BotsDAO
from app.clients.dao import ClientsDAO
from app.contacts.dao import ContactsDAO
from app.contacts.schemas import SContacts
from app.contacts.utils import add_contact_for_operator
from app.database import DbSession
from app.exceptions import NotBotWithThisId, NotOperatorForYourContact

router = APIRouter(
    prefix="/contacts",
    tags=["Обращения/Контакты"],
)


@router.post("/add")
async def add_contact(session: DbSession, client_email: str, bot_id: int) -> SContacts:
    bot = await BotsDAO.find_by_id(session=session, model_id=bot_id)
    if not bot:
        raise NotBotWithThisId

    if bot.operators == {}:
        raise NotOperatorForYourContact

    client = await ClientsDAO.find_one_or_none(session=session, email=client_email)
    if not client:
        client = await ClientsDAO.add(
            session=session,
            email=client_email,
        )

    new_contact = await add_contact_for_operator(
        session=session,
        operators=bot.operators.keys(),
        weights=bot.operators.values(),
        client_id=client.id,  # pyright: ignore [reportOptionalMemberAccess]
        bot_id=bot_id,
    )
    if not new_contact:
        raise NotOperatorForYourContact

    return new_contact


@router.get("/{client_id}")
async def get_contacts_by_client_id(
    session: DbSession, client_id: int
) -> List[SContacts]:
    contacts = await ContactsDAO.find_all(session=session, client_id=client_id)

    return contacts


@router.get("/all/")
async def get_all_contacts(session: DbSession) -> List[SContacts]:
    all_contacts = await ContactsDAO.find_all(session=session)

    return all_contacts


@router.delete("/del")
async def delete_contact(session: DbSession, contact_id: int) -> None:
    await ContactsDAO.delete(session=session, id=contact_id)
