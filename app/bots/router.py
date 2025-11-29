# THIRDPARTY
from fastapi import APIRouter

# FIRSTPARTY
from app.bots.dao import BotsDAO
from app.bots.schemas import SBots
from app.database import DbSession
from app.exceptions import NotBotWithThisId, NotOperatorWithThisId
from app.operators.dao import OperatorsDAO

router = APIRouter(
    prefix="/bots",
    tags=["Боты/Источники"],
)


@router.post("/add")
async def add_bot(session: DbSession) -> SBots:
    bot = await BotsDAO.add(session=session)
    return bot


@router.get("/{bot_id}")
async def get_bot_by_id(session: DbSession, bot_id: int) -> SBots:
    bot = await BotsDAO.find_by_id(session=session, model_id=bot_id)
    if not bot:
        raise NotBotWithThisId
    return bot


@router.patch("/update_operators")
async def update_operators(
    session: DbSession, bot_id: int, operator_id: int, weight: int
) -> SBots:
    operator = await OperatorsDAO.find_by_id(session=session, model_id=operator_id)
    if not operator:
        raise NotOperatorWithThisId

    bot = await BotsDAO.find_by_id(session=session, model_id=bot_id)
    if not bot:
        raise NotBotWithThisId

    updated_bot = await BotsDAO.update_bot_operators(
        session=session, bot_id=bot_id, operator_id=operator_id, weight=weight
    )

    return updated_bot
