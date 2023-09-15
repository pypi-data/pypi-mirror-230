import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from spartaORM.models.base import Base


class SegmentMetricsModel(Base):
    __tablename__ = "athlete"
    __table_args__ = {"extend_existing": True}

    id = Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id = Column("athlete_id", Integer, ForeignKey("athlete.id"), nullable=False)
    race_id = Column("race_id", UUID, ForeignKey("race.id"), nullable=False)
    start_segment = Column("start_segment", Integer, nullable=False)
    end_segment = Column("end_segment", Integer, nullable=False)
    velocity = Column("velocity", Float, nullable=True)
    stroke_rate = Column("stroke_rate", Float, nullable=True)
    dps = Column("dps", Float, nullable=True)
    strokes = Column("strokes", Integer, nullable=True)
    kicks = Column("kicks", Integer, nullable=True)
    breaths = Column("breaths", Integer, nullable=True)
    breakout = Column("breakout", Integer, nullable=True)
    in_time = Column("in_time", Float, nullable=True)
    out_time = Column("out_time", Float, nullable=True)
    turn_time = Column("turn_time", Float, nullable=True)
    turn_index = Column("turn_index", Float, nullable=True)
    split_time = Column("split_time", DateTime, nullable=False)
    lap_time = Column("lap_time", Float, nullable=True)
