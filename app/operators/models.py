# THIRDPARTY
from sqlalchemy.orm import Mapped, mapped_column

# FIRSTPARTY
from app.database import Base


class Operators(Base):
    __tablename__ = "operators"

    status: Mapped[int] = mapped_column(default=0, nullable=False)
    limit_of_contacts: Mapped[int] = mapped_column(nullable=False)
