# THIRDPARTY
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

# FIRSTPARTY
from app.database import Base


class Bots(Base):
    __tablename__ = "bots"

    operators: Mapped[dict[int, int]] = mapped_column(JSON, nullable=True, default={})
