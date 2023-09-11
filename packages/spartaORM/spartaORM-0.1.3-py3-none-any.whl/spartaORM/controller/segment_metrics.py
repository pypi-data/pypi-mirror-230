from datetime import datetime
from spartaORM.controller.base import BaseController
from spartaORM.models.segment_metrics import SegmentMetricsModel


class SegmentMetrics(BaseController):
    def __init__(self, database_url: str) -> None:
        super().__init__(database_url=database_url)

    def add(
        self,
        athlete_id: int,
        race_id: int,
        start_segment: int,
        end_segment: int,
        velocity: float,
        stroke_rate: float,
        dps: float,
        strokes: int,
        kicks: int,
        breaths: int,
        breakout: int,
        in_time: float,
        out_time: float,
        turn_time: float,
        turn_index: float,
        split_time: datetime,
        lap_time: float,
    ):
        segment_metrics_entry = SegmentMetricsModel(
            athlete_id=athlete_id,
            race_id=race_id,
            start_segment=start_segment,
            end_segment=end_segment,
            velocity=velocity,
            stroke_rate=stroke_rate,
            dps=dps,
            strokes=strokes,
            kicks=kicks,
            breaths=breaths,
            breakout=breakout,
            in_time=in_time,
            out_time=out_time,
            turn_time=turn_time,
            turn_index=turn_index,
            split_time=split_time,
            lap_time=lap_time,
        )

        return self.create_entry(segment_metrics_entry)
