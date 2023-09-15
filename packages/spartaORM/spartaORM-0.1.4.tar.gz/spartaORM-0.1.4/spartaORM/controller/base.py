from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker


class BaseController:
    __tablename__: str

    def __init__(self, database_url):
        self._session_maker = sessionmaker(
            bind=create_engine(
                database_url,
                pool_recycle=1,
                pool_size=30,
                max_overflow=50,
                pool_pre_ping=True,
            )
        )

    def _create_session(func):
        def wrapper(self, *args, **kwargs):
            try:
                self._session = self._session_maker()

                result = func(self, *args, **kwargs)

                self._session.close()

                return result
            except exc.IntegrityError as error:
                self._session.close()

                raise Exception(error)

        return wrapper

    @_create_session
    def create_entry(self, entry):
        self._session.add(entry)
        self._session.commit()

        return entry.id
