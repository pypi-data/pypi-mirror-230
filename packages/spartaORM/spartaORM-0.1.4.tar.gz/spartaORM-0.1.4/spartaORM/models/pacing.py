import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, Float, Integer
from spartaORM.models.base import Base


class PacingModel(Base):
    __tablename__ = "pacing"
    __table_args__ = {"extend_existing": True}

    id = Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id = Column("athlete_id", Integer, ForeignKey("athlete.id"), nullable=False)
    race_id = Column("race_id", UUID, ForeignKey("race.id"), nullable=False)
    out_time = Column("out_time", Float, nullable=False)
    back_time = Column("back_time", Float, nullable=False)
    drop_off = Column("drop_off", Float, nullable=False)
    out_percent = Column("out_percent", Float, nullable=False)
    back_percent = Column("back_percent", Float, nullable=False)
