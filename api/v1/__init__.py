from fastapi import APIRouter

from api.v1.information import router as information_router
from api.v1.reports import router as reports_router
from api.v1.transactions import router as transactions_router


# AS: Короче, такая тема. Я сам делал также, сначала использовал API Router, как Blue print'ы в Flask
# AS: Но оказалось, что их использование несет ряд ограничений (или усложнений), вроде использования Middleware
# AS: Так что фиг знает, стоит ли его использовать везде. Может и стоит, гибкости будет больше, но есть и минусы.
router = APIRouter(prefix="/v1")
router.include_router(transactions_router)
router.include_router(reports_router)
router.include_router(information_router)
