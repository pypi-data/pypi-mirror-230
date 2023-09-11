import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Float, Integer, ForeignKey
from spartaORM.models.base import Base


class SummaryMetricsModel(Base):
    __tablename__ = "athlete"
    __table_args__ = {"extend_existing": True}

    id = Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id = Column("athlete_id", Integer, ForeignKey("athlete.id"), nullable=False)
    race_id = Column("race_id", UUID, ForeignKey("race.id"), nullable=False)
    total_time = Column("total_time", Float, nullable=False)
    total_skill_time = Column("total_skill_time", Float, nullable=False)
    total_free_swim_time = Column("total_free_swim_time", Float, nullable=False)
    breakout_distance = Column("breakout_distance", Float, nullable=False)
    breakout_time = Column("breakout_time", Float, nullable=False)
    first_15_meter = Column("first_15_meter", Float, nullable=False)
    first_25_meter = Column("first_25_meter", Float, nullable=False)
    last_5_meter = Column("last_5_meter", Float, nullable=False)
    finish_stroke_rate = Column("finish_stroke_rate", Float, nullable=False)
