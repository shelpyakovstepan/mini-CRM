# THIRDPARTY
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

# FIRSTPARTY
from app.bots.models import Bots
from app.dao.base import BaseDao


class BotsDAO(BaseDao):
    model = Bots

    @classmethod
    async def update_bot_operators(
        cls, session: AsyncSession, bot_id: int, operator_id: int, weight: int
    ):
        get_bot_operators_query = (
            select(Bots.operators).select_from(Bots).where(Bots.id == bot_id)
        )

        bot_operators = await session.execute(get_bot_operators_query)
        bot_operators = bot_operators.scalar()

        bot_operators[operator_id] = weight  # pyright: ignore [reportOptionalSubscript]

        bot_with_new_operators_info_query = (
            update(Bots)
            .where(Bots.id == bot_id)
            .values(operators=bot_operators)
            .returning(Bots)
        )

        bot_with_new_operators_info = await session.execute(
            bot_with_new_operators_info_query
        )

        return bot_with_new_operators_info.scalar()
