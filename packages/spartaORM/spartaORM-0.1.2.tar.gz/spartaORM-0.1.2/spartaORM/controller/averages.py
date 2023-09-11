from spartaORM.controller.base import BaseController
from spartaORM.models.averages import AveragesModel


class Averages(BaseController):
    def __init__(self, database_url: str) -> None:
        super().__init__(database_url=database_url)

    def add(
        self,
        athlete_id: int,
        race_id: int,
        velocity: float,
        stroke_rate: float,
        dps: float,
        in_time: float,
        out_time: float,
        turn_time: float,
        turn_index: float,
    ):
        averages_entry = AveragesModel(
            athlete_id,
            race_id,
            velocity,
            stroke_rate,
            dps,
            in_time,
            out_time,
            turn_time,
            turn_index,
        )

        return self.create_entry(averages_entry)
