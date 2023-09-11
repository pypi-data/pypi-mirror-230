import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, Enum, Date, Boolean, ForeignKey
from spartaORM.models.base import Base

from spartaORM.enums.swim import (
    SwimType,
    StrokeType,
    RelayLeg,
    RelayType,
    PoolType,
    AgeGroup,
)


class RaceModel(Base):
    __tablename__ = "race"
    __table_args__ = {"extend_existing": True}

    id = Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id = Column("athlete_id", Integer, ForeignKey("athlete.id"), nullable=False)
    swim_date = Column("swim_date", String, nullable=False)
    competition_id = Column("competition_id", String, nullable=False)
    event_id = Column("event_id", Integer, nullable=False)
    venue_id = Column("venue_id", String, nullable=False)
    swim_type = Column(
        "swim_type",
        Enum(SwimType, values_callable=lambda x: [str(e.value) for e in SwimType]),
        nullable=False,
    )
    stroke_type = Column(
        "stroke_type",
        Enum(StrokeType, values_callable=lambda x: [str(e.value) for e in StrokeType]),
        nullable=False,
    )
    event_distance = Column("event_distance", Integer, nullable=False)
    pool_type = Column(
        "pool_type",
        Enum(PoolType, values_callable=lambda x: [str(e.value) for e in PoolType]),
        nullable=False,
    )
    age_group = Column(
        "age_group",
        Enum(AgeGroup, values_callable=lambda x: [str(e.value) for e in AgeGroup]),
        nullable=False,
    )
    is_relay = Column("is_relay", Boolean, nullable=False)
    relay_type = Column(
        "relay_type",
        Enum(RelayType, values_callable=lambda x: [str(e.value) for e in RelayType]),
        nullable=True,
    )
    relay_leg = Column(
        "relay_leg",
        Enum(RelayLeg, values_callable=lambda x: [str(e.value) for e in RelayLeg]),
        nullable=True,
    )
    created_time = Column("created_time", Date, nullable=False)
    online_video_filename = Column("online_video_filename", String, nullable=False)
