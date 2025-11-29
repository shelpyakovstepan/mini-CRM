# STDLIB
import random

# THIRDPARTY
from sqlalchemy.ext.asyncio import AsyncSession

# FIRSTPARTY
from app.contacts.dao import ContactsDAO


async def weighted_random_choice(operators, weights):
    """
    Случайный выбор оператора с учетом весов
    """
    if not operators:
        return
    return int(random.choices(operators, weights=weights, k=1)[0])


async def add_contact_for_operator(
    session: AsyncSession,
    operators: list,
    weights: list,
    client_id: int,
    bot_id: int,
):
    operators = [o for o in operators]
    sum_weights = sum(weights)
    weights_for_choice = [w / sum_weights * 100 for w in weights]
    operator_id = await weighted_random_choice(
        operators=operators, weights=weights_for_choice
    )
    if operator_id is None:
        return

    new_contact = await ContactsDAO.add_new_contact(
        session=session,
        client_id=client_id,
        bots_id=bot_id,
        operator_id=operator_id,
    )
    while new_contact is None:
        index = operators.index(str(operator_id))
        operators.remove(str(operator_id))
        weight = weights_for_choice.pop(index)
        sum_weights -= weight
        operator_id = await weighted_random_choice(
            operators=operators, weights=weights_for_choice
        )
        if operator_id is None:
            break
        new_contact = await ContactsDAO.add_new_contact(
            session=session,
            client_id=client_id,
            bots_id=bot_id,
            operator_id=operator_id,
        )

    return new_contact
