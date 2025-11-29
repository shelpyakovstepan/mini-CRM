# THIRDPARTY
from sqlalchemy.orm import Mapped, mapped_column

# FIRSTPARTY
from app.database import Base


class Clients(Base):
    __tablename__ = "clients"

    email: Mapped[str] = mapped_column(unique=True, nullable=False)
