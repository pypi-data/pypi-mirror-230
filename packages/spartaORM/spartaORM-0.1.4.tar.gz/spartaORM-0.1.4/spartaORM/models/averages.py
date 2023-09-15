import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Float, Integer, ForeignKey
from spartaORM.models.base import Base


class AveragesModel(Base):
    __tablename__ = "averages"
    __table_args__ = {"extend_existing": True}

    id = Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id = Column("athlete_id", Integer, ForeignKey("athlete.id"), nullable=False)
    race_id = Column("race_id", UUID, ForeignKey("race.id"), nullable=False)
    velocity = Column("velocity", Float, nullable=False)
    stroke_rate = Column("stroke_rate", Float, nullable=False)
    dps = Column("dps", Float, nullable=False)
    in_time = Column("in_time", Float, nullable=False)
    out_time = Column("out_time", Float, nullable=False)
    turn_time = Column("turn_time", Float, nullable=False)
    turn_index = Column("turn_index", Float, nullable=False)
