# THIRDPARTY
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

# FIRSTPARTY
from app.database import Base


class Contacts(Base):
    __tablename__ = "contacts"

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    bots_id: Mapped[int] = mapped_column(ForeignKey("bots.id"), nullable=False)
    operator_id: Mapped[int] = mapped_column(ForeignKey("operators.id"), nullable=False)
