# THIRDPARTY
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

# FIRSTPARTY
from app.contacts.models import Contacts
from app.dao.base import BaseDao
from app.operators.models import Operators


class ContactsDAO(BaseDao):
    model = Contacts

    @classmethod
    async def add_new_contact(
        cls,
        session: AsyncSession,
        client_id: int,
        bots_id: int,
        operator_id: int,
    ):
        operator_query = select(Operators).where(Operators.id == operator_id)
        operator = await session.execute(operator_query)

        operator = operator.scalar()
        if (
            operator.status == 0  # pyright: ignore [reportOptionalMemberAccess]
        ):  # если статус оператора 0 - то он неактивен, и следовательно, не может принимать обращения
            return

        get_operators_contacts_query = select(Contacts).where(
            Contacts.operator_id == operator_id
        )

        get_operators_contacts = await session.execute(get_operators_contacts_query)

        if (
            len(get_operators_contacts.scalars().all()) == operator.limit_of_contacts  # pyright: ignore [reportOptionalMemberAccess]
        ):  # если кол-во действительных обращений для одного оператора уже равно его лимиту, то он не может принимать обращения
            return

        new_contact_query = (
            insert(Contacts)
            .values(
                client_id=client_id,
                bots_id=bots_id,
                operator_id=operator_id,
            )
            .returning(Contacts)
        )

        new_contact = await session.execute(new_contact_query)

        return new_contact.scalar()
