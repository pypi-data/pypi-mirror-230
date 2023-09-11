from spartaORM.controller.base import BaseController
from spartaORM.models.official_results import OfficialResultsModel


class OfficialResults(BaseController):
    def __init__(self, database_url: str) -> None:
        super().__init__(database_url=database_url)

    def add(
        self,
        athlete_id: int,
        race_id: int,
        block_time: int,
        total_time_milliseconds: int,
        split_matrix,
    ):
        official_results_entry = OfficialResultsModel(
            athlete_id, race_id, block_time, total_time_milliseconds, split_matrix
        )

        return self.create_entry(official_results_entry)
