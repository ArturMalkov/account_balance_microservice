import sqlalchemy as sa
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from settings import settings


# TODO: logging


# AS: Что-то слишком длинная строка
# AS: Echo = True вместо хардкода надо в конфиг запихать, имхо
engine: sa.engine.Engine = sa.create_engine(settings.DATABASE_URL, echo=True, json_serializer=jsonable_encoder)

# AS: Имхо, лишний перевод строки
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
        # AS: Контекстный менеджер должен обеспечивать закрытие сессии сам по себе. Он же для этого и нужен.
        # AS: Либо использовать try с обработкой исключений, либо with.
        finally:
            session.close()
