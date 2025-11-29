# STDLIB
from contextlib import asynccontextmanager
from typing import AsyncIterator

# THIRDPARTY
from fastapi import FastAPI

# FIRSTPARTY
from app.bots.router import router as bots_router
from app.clients.router import router as clients_router
from app.contacts.router import router as contacts_router
from app.database import check_db_connection
from app.operators.router import router as operators_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await check_db_connection()

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(operators_router)
app.include_router(bots_router)
app.include_router(contacts_router)
app.include_router(clients_router)
