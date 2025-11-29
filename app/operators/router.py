# STDLIB
from typing import List, Literal

# THIRDPARTY
from fastapi import APIRouter, Query

# FIRSTPARTY
from app.database import DbSession
from app.exceptions import NotOperatorWithThisId
from app.operators.dao import OperatorsDAO
from app.operators.schemas import SOperators

router = APIRouter(
    prefix="/operators",
    tags=["Операторы"],
)


@router.post("/add")
async def add_operator(
    session: DbSession, limit_of_contacts: int = Query(gt=0)
) -> SOperators:
    operator = await OperatorsDAO.add(
        session=session, limit_of_contacts=limit_of_contacts
    )
    return operator


@router.get("/all")
async def get_all_operators(session: DbSession) -> List[SOperators]:
    operators = await OperatorsDAO.find_all(session=session)

    return operators


@router.patch("/update_status")
async def update_operator_status(
    session: DbSession,
    operator_id: int,
    status: int = Literal[0, 1],  # pyright: ignore [reportArgumentType]
) -> SOperators:
    operator = await OperatorsDAO.find_by_id(session=session, model_id=operator_id)
    if not operator:
        raise NotOperatorWithThisId

    operator = await OperatorsDAO.update(
        session=session, model_id=operator_id, status=status
    )
    return operator


@router.patch("/update_limit")
async def update_operator_limit_of_contacts(
    session: DbSession,
    operator_id: int,
    limit_of_contacts: int = Query(gt=0),
) -> SOperators:
    operator = await OperatorsDAO.find_by_id(session=session, model_id=operator_id)
    if not operator:
        raise NotOperatorWithThisId

    operator = await OperatorsDAO.update(
        session=session, model_id=operator_id, limit_of_contacts=limit_of_contacts
    )
    return operator
