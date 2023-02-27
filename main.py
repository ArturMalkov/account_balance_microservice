# AS: Импорты отсортированы некорректно
import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from settings import settings
from api.v1 import router


# AS: Почему это в main?
TAGS_METADATA = [
    {
        "name": "transactions",
        "description": "Account balance/transactions functionality",
    },
    {"name": "reports", "description": "Accounting reports functionality"},
    {
        "name": "information",
        "description": "Account balance/transactions information functionality",
    },
]

# AS: Почему вырублен логгер
# logger = ...

# AS: Если у тебя есть метадата в виде отдельного json'а, то можно туда закинуть тайтлы и описания, чтобы они в мейне не мешались
app = FastAPI(
    title="Account Balance Microservice",
    description="Account Balance Microservice - MORE DETAILS TO FOLLOW",
    version="1.0.0",
    openapi_tags=TAGS_METADATA,
)

# AS: Зачем здесь пропуск строки?
app.include_router(router)


@app.on_event("startup")
def startup_event():
    # logger.info("Starting up...")
    pass


@app.on_event("shutdown")
def shutdown_event():
    # logger.info("Shutting down...")
    pass


@app.exception_handler(ValueError)
def value_error_exception_handler(request: Request, exc: ValueError) -> JSONResponse:
    # TODO: add logging functionality

    # AS: Зачем здесь пропуск строки?
    # AS: Почему статус код 422, а не 500? 422 - это ж довольно частный кейс, 500 - более общий.
    return JSONResponse(status_code=422, content={"message": str(exc)})


# AS: Почему в мейне есть отдельный endpoint? Как по-мне, так ему здесь не место.
@app.get("/")
def welcome_page(request: Request) -> JSONResponse:
    return JSONResponse(
        content={
            "Swagger UI Documentation": "Please proceed to '/docs' to access OpenAPI documentation (with Swagger UI).",
            "ReDoc Documentation": "Please proceed to '/redoc' to access OpenAPI documentation (with Swagger UI).",
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
    )
