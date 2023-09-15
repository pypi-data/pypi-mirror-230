import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, ForeignKey, JSON
from spartaORM.models.base import Base


class OfficialResultsModel(Base):
    __tablename__ = "official_results"
    __table_args__ = {"extend_existing": True}

    id = Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id = Column("athlete_id", Integer, ForeignKey("athlete.id"), nullable=False)
    race_id = Column("race_id", UUID, ForeignKey("race.id"), nullable=False)
    block_time = Column("block_time", Integer, nullable=False)
    total_time_milliseconds = Column("total_time_milliseconds", Integer, nullable=False)
    split_matrix = Column("split_matrix", JSON, nullable=False)
