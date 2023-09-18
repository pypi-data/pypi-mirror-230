from sqlalchemy.orm import Session

from fastutils_hmarcuzzo.common.database.sqlalchemy.session import DatabaseSessionFactory


class GetDB:
    def __int__(self, database_url: str, app_tz: str = "UTC"):
        self.session = DatabaseSessionFactory(database_url, app_tz)

    def get_db(self) -> Session:
        db: Session = self.session.get_session()
        try:
            yield db
        finally:
            db.close()
