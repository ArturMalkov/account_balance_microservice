import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from services.reports import ReportsService
from settings import settings


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/consolidated/monthly")
def get_monthly_accounting_report(
        year: int = Query(gt=settings.YEAR_REPORTS_ARE_AVAILABLE_FROM, le=datetime.datetime.now().year),
        month: int = Query(ge=1, le=12),
        reports_service: ReportsService = Depends()
) -> StreamingResponse:
    """
    Returns csv report with total revenues for each service rendered in the requested period.
    Format: service name, total revenues in the reporting period.
    """
    report = reports_service.prepare_monthly_accounting_report_in_csv(year, month)
    return StreamingResponse(
        report,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=report_{year}-{month}.csv"},
    )
