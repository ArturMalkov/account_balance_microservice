import sqlalchemy as sa
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from settings import settings


# TODO: logging


engine: sa.engine.Engine = sa.create_engine(settings.DATABASE_URL, echo=True, json_serializer=jsonable_encoder)

Session: sessionmaker = sessionmaker(bind=engine)


# Dependency to be injected
def get_db_session() -> Session:
    with Session() as session:
        try:
            yield session
        except SQLAlchemyError as sql_err:
            raise sql_err  # TODO: logging here?
        except HTTPException as http_err:
            raise http_err  # TODO: logging here?
        finally:
            session.close()
