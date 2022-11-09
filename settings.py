from dotenv import load_dotenv

from pydantic import BaseSettings


load_dotenv()  # do we need it here???


class Settings(BaseSettings):
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 8000

    DATABASE_HOST: str = ""
    DATABASE_PORT: int = 5432
    POSTGRES_USERNAME: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DATABASE_NAME: str = ""
    # DATABASE_URL: str = (
    #     f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/"
    #     f"{POSTGRES_DATABASE_NAME}"
    # )
    # DATABASE_URL: str = "postgresql://postgres:Kleopatra2003!@127.0.0.1:5433/account_balances"
    DATABASE_URL: str = "postgresql://postgres:Kleopatra2003!@127.0.0.1:5433/account_balances"

    YEAR_REPORTS_ARE_AVAILABLE_FROM: int = 2020  # let's assume this is the year the company was founded
    NUMBER_OF_RESULTS_PER_PAGE: int = 5


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")
