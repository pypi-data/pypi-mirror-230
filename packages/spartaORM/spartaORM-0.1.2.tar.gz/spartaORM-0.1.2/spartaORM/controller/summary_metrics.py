from spartaORM.controller.base import BaseController
from spartaORM.models.summary_metrics import SummaryMetricsModel


class SummaryMetrics(BaseController):
    def __init__(self, database_url: str) -> None:
        super().__init__(database_url=database_url)

    def add(
        self,
        athlete_id: int,
        race_id: int,
        total_time: float,
        total_skill_time: float,
        total_free_swim_time: float,
        breakout_distance: float,
        breakout_time: float,
        first_15_meter: float,
        last_15_meter: float,
        last_5_meter: float,
        finish_stroke_rate: float,
    ):
        summary_metrics_entry = SummaryMetricsModel(
            athlete_id,
            race_id,
            total_time,
            total_skill_time,
            total_free_swim_time,
            breakout_distance,
            breakout_time,
            first_15_meter,
            last_15_meter,
            last_5_meter,
            finish_stroke_rate,
        )

        return self.create_entry(summary_metrics_entry)
