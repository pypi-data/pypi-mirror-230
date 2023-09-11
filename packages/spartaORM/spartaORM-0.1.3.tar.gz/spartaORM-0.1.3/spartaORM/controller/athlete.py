from spartaORM.controller.base import BaseController
from spartaORM.models.athlete import AtheleteModel


class Athlete(BaseController):
    def __init__(self, database_url: str) -> None:
        super().__init__(database_url=database_url)

    def add(
        self,
        id: int,
        user_name: str,
        first_name: str,
        last_name: str,
        sex,
        known_as: str,
    ):
        athlete_entry = AtheleteModel(
            id=id,
            user_name=user_name,
            first_name=first_name,
            last_name=last_name,
            sex=sex,
            known_as=known_as,
        )

        return self.create_entry(athlete_entry)

    @BaseController._create_session
    def fetch_athlete(self, **kwargs):
        query_athletes = self._session.query(AtheleteModel)

        for key, value in kwargs.items():
            if key == "id":
                query_athletes = query_athletes.filter(AtheleteModel.id == value)
            elif key == "user_name":
                query_athletes = query_athletes.filter(AtheleteModel.user_name == value)
            elif key == "known_as":
                query_athletes = query_athletes.filter(AtheleteModel.known_as == value)

        athletes_list = query_athletes.all()

        return athletes_list
