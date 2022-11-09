from fastapi import APIRouter

from api.v1.information import router as information_router
from api.v1.reports import router as reports_router
from api.v1.transactions import router as transactions_router


router = APIRouter(prefix="/v1")
router.include_router(transactions_router)
router.include_router(reports_router)
router.include_router(information_router)
