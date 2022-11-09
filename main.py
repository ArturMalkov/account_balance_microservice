import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from settings import settings
from api.v1 import router


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

# logger = ...

app = FastAPI(
    title="Account Balance Microservice",
    description="Account Balance Microservice - MORE DETAILS TO FOLLOW",
    version="1.0.0",
    openapi_tags=TAGS_METADATA,
)

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

    return JSONResponse(status_code=422, content={"message": str(exc)})


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
