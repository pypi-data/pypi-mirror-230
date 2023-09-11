from sqlalchemy import Column, Enum, String, Integer
from spartaORM.models.base import Base

from spartaORM.enums.sex import Sex


class AtheleteModel(Base):
    __tablename__ = "athlete"
    __table_args__ = {"extend_existing": True}

    id = Column("id", Integer, primary_key=True)
    user_name = Column("user_name", String(100), nullable=False)
    first_name = Column("first_name", String(100), nullable=False)
    last_name = Column("last_name", String(100), nullable=False)
    sex = Column(
        "sex",
        Enum(Sex, values_callable=lambda x: [str(e.value) for e in Sex]),
        nullable=False,
    )
    known_as = Column("known_as", String(100), nullable=False)
