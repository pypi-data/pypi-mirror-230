from datetime import date
from spartaORM.controller.base import BaseController
from spartaORM.models.race import RaceModel


class Race(BaseController):
    def __init__(self, database_url: str) -> None:
        super().__init__(database_url=database_url)

    def add(
        self,
        swim_date: str,
        athlete_id: int,
        event_id: int,
        competition_id: int,
        swim_type: str,
        stroke_type: str,
        relay_leg: str,
        relay_type: str,
        pool_type: str,
        age_group: str,
        event_distance: int,
        created_time: date,
        online_video_filename: str,
        venue_id: int,
        is_relay: bool = False,
    ):
        race_entry = RaceModel(
            swim_date=swim_date,
            athlete_id=athlete_id,
            event_id=event_id,
            competition_id=competition_id,
            swim_type=swim_type,
            stroke_type=stroke_type,
            relay_leg=relay_leg,
            relay_type=relay_type,
            pool_type=pool_type,
            age_group=age_group,
            event_distance=event_distance,
            created_time=created_time,
            online_video_filename=online_video_filename,
            venue_id=venue_id,
            is_relay=is_relay,
        )

        return self.create_entry(race_entry)
