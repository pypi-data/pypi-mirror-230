from spartaORM.controller.base import BaseController
from spartaORM.models.pacing import PacingModel


class Pacing(BaseController):
    def __init__(self, database_url: str) -> None:
        super().__init__(database_url=database_url)

    def add(
        self,
        athlete_id: int,
        race_id: int,
        out_time: float,
        back_time: float,
        drop_off: float,
        out_percent: float,
        back_percent: float,
    ):
        pacing_entry = PacingModel(
            athlete_id,
            race_id,
            out_time,
            back_time,
            drop_off,
            out_percent,
            back_percent,
        )

        return self.create_entry(pacing_entry)
