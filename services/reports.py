import csv
import calendar
import datetime
from collections import defaultdict
from decimal import Decimal
from io import StringIO

from fastapi import status, Depends, HTTPException
from sqlalchemy.orm import Session

from exceptions import ExceptionDescription
from storage import tables
from storage.database import get_db_session
from storage.tables import TransactionType


class ReportsService:
    def __init__(self, db_session: Session = Depends(get_db_session)) -> None:
        self.db_session = db_session

    def prepare_monthly_accounting_report_in_csv(
        self,
        year: int,
        month: int,
    ) -> StringIO:
        output = StringIO()  # to create a file-like object in memory
        writer = csv.writer(
            output,
            lineterminator="\n",
        )

        field_names = ["Service Name", f"Total Revenue in the period (YYYY-MM) {year}-{month}"]
        writer.writerow(field_names)

        services_revenue_info = self._calculate_revenue_from_services(year, month)
        writer.writerows(services_revenue_info.items())

        output.seek(0)

        return output

    def _calculate_revenue_from_services(
        self, year: int, month: int
    ) -> defaultdict[str, Decimal]:
        """
        Calculates revenue for each service rendered in the reporting period.
        More detail.
        Returns a dictionary which maps service name with total revenue from it in the period.
        """
        number_of_days_in_the_reporting_period = calendar.monthrange(year, month)[1]
        reporting_period_start = datetime.date(year, month, 1)
        reporting_period_end = datetime.date(year, month, number_of_days_in_the_reporting_period)

        services_with_revenues_in_the_period = defaultdict(lambda: Decimal(0))

        payment_transactions_in_the_period = [transaction for transaction in
                                              self.db_session.query(tables.Transaction).all()
                                              if transaction.type == TransactionType.PAYMENT_TO_COMPANY
                                              and reporting_period_start <= transaction.date.date()
                                              <= reporting_period_end]

        for transaction in payment_transactions_in_the_period:
            for ordered_service in transaction.order.items:
                services_with_revenues_in_the_period[ordered_service.service.name] \
                    += ordered_service.quantity * ordered_service.service.price

        if not services_with_revenues_in_the_period:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,  # or 422?
                detail=ExceptionDescription.NO_SERVICES_RENDERED_IN_THE_PERIOD.value,
            )

        return services_with_revenues_in_the_period
