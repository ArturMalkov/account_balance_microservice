import sqlalchemy as sa
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Query, Session

from exceptions import ExceptionDescription
from messages import MessageDescription
from models.information import UserAccountOut
from settings import settings
from storage import tables
from storage.tables import AccountType
from storage.database import get_db_session


class InformationService:
    """Responsible for working with user accounts' data"""

    def __init__(self, db_session: Session = Depends(get_db_session)):
        self.db_session = db_session

    # AS: Продублирую из tables.
    # AS: Тут один из самых важных архитектурных вопросов для меня. Должен ли у аккаунта хранится баланс?
    # AS: Мой ответ одназначный - нет, не должен. И насколько я знаю почти никто его не хранит в таком виде.
    # AS: Тут можно рассуждать, но риски неконсистентности высокие. Бэст прэктиз - собирать динамически.
    def get_account_balance_info(self, user_id: int) -> list[UserAccountOut]:
        """
        Returns info on user's regular and reserve accounts.
        """
        regular_account_balance_info = self._get_user_account_by_user_id(user_id, AccountType.REGULAR)
        reserve_account_balance_info = self._get_user_account_by_user_id(user_id, AccountType.RESERVE)

        return [regular_account_balance_info, reserve_account_balance_info]

    # AS: Вопрос (я сам не знаю) стоит ли дублировать в функции, которую вызывает fastapi, значения по умолчанию?
    # AS: В такой случае придется в случае чего придется их править в двух местах, а значит можно накосячить.
    def get_account_transactions_info(
        self,
        user_id: int,
        *,
        page: int | None = None,
        sort_by_amount: bool = False,
        sort_by_date: bool = False
    ) -> list[tables.Transaction] | JSONResponse:
        """
        Returns a list of transactions with description on where and why the funds
        were credited/debited from the account balance.
        Sorting (by date and amount) and pagination of results are provided as an option.
        """
        user = self._get_user_by_user_id(user_id)
        if not user.accounts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ExceptionDescription.ACCOUNT_DOES_NOT_EXIST.value,
            )

        user_orders_ids = [order.id for order in user.orders]

        # AS: Как я понимаю, тут ты целенаправленно не успользуешь relationship'ы, как выше?
        # AS: В целом, в рамках того, как реализовано, это ок
        # AS: Но relationship'ы такая крутая и удобная штука, что я их стараюсь использовать по максимуму
        account_transactions = self.db_session.query(
            tables.Transaction)\
            .filter(
            sa.or_(
                tables.Transaction.from_user_id == user_id,
                tables.Transaction.to_user_id == user_id,
                tables.Transaction.order_id.in_(user_orders_ids)
            )
        )

        if not account_transactions:
            return JSONResponse(
                content={"message": MessageDescription.NO_TRANSACTIONS_AVAILABLE.value}
            )

        # AS: Я бы сортировки делал в рамках одной функции
        if sort_by_date:
            account_transactions = self._sort_rows_by_date_column(tables.Transaction, account_transactions)

        if sort_by_amount:
            account_transactions = self._sort_rows_by_amount_column(tables.Transaction, account_transactions)

        if page:
            account_transactions = self._get_table_pagination_results(account_transactions, page_number=page)

        return account_transactions.all()

    def _get_user_account_by_user_id(
        self,
        user_id: int,
        account_type: AccountType,
    ) -> tables.UserAccount:
        """
        Returns account of a specified type (regular/reserve) of a particular user.
        """
        # AS: Вроде это лишний вызов (и сама функция лишняя, как по мне).
        # AS: Ты фактически делаешь два обращения к БД там, где достаточно одного.
        # AS: Можно просто убрать эту строку и ничего не поменяется (проверка есть ниже).
        self._raise_error_if_user_does_not_exist(user_id)

        account = (
            self.db_session.query(tables.UserAccount)
            .filter(
                sa.and_(
                    tables.UserAccount.user_id == user_id,
                    tables.UserAccount.type == account_type,
                )
            )
            .first()
        )
        if not account:
            # AS: Подобные блоки много раз повторяются.
            # AS: Я бы: 1. либо создал отдельные экспешены
            # AS: 2. Либо сделал под это дело декоратор (если возможно)
            # AS: 3. Либо в крайнем случае сократил бы 4 строки до 2-х. Т.е. так:
            # AS: exc_msg = ExceptionDescription.ACCOUNT_DOES_NOT_EXIST.value
            # AS: HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc_msg)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,  # 422?
                detail=ExceptionDescription.ACCOUNT_DOES_NOT_EXIST.value,
            )

        return account

    def _get_user_accounts_by_order_id(self, order_id: int) -> list[tables.UserAccount]:
        """
        Returns both regular and reserve accounts of a particular user.
        """
        order = self.db_session.query(tables.Order).filter(tables.Order.id == order_id).first()
        user_accounts = order.user.accounts

        if not user_accounts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ExceptionDescription.ACCOUNT_DOES_NOT_EXIST.value,
            )

        return user_accounts

    def _get_company_account_by_company_account_id(self, company_account_id: int) -> tables.CompanyAccount:
        # AS: Зачем так сложно? Если по id надо, то можно get использовать вместо filter.
        company_account = self.db_session.query(tables.CompanyAccount)\
            .filter(tables.CompanyAccount.id == company_account_id).first()

        if not company_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,  # 422?
                detail=ExceptionDescription.COMPANY_ACCOUNT_DOES_NOT_EXIST.value
            )

        return company_account

    def _get_user_by_user_id(self, user_id: int) -> tables.User:
        self._raise_error_if_user_does_not_exist(user_id)

        user = self.db_session.query(tables.User).filter(tables.User.id == user_id).first()
        return user

    # Мне кажется, что эта функция не нужна
    def _raise_error_if_user_does_not_exist(
        self, user_id: int
    ) -> None:
        user = self.db_session.query(tables.User).filter(tables.User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,  # 422?
                detail=ExceptionDescription.USER_DOES_NOT_EXIST.value
            )

    @staticmethod
    def _get_table_pagination_results(
        selected_rows: Query, *, page_number: int
    ) -> Query:
        pagination_results = selected_rows\
            .limit(settings.NUMBER_OF_RESULTS_PER_PAGE)\
            .offset((page_number - 1) * settings.NUMBER_OF_RESULTS_PER_PAGE)

        if not pagination_results.all():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ExceptionDescription.RESULTS_NOT_AVAILABLE_FOR_THIS_PAGE.value,
            )

        return pagination_results

    @staticmethod
    def _sort_rows_by_date_column(table: sa.Table, selected_rows: Query) -> Query:
        """Only works with tables with 'date' field present"""
        if not hasattr(table, "date"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ExceptionDescription.RESOURCE_CANNOT_BE_SORTED_BY_DATE.value,
            )

        sorted_by_date = selected_rows.order_by(table.date.desc())
        return sorted_by_date

    @staticmethod
    def _sort_rows_by_amount_column(table: sa.Table, selected_rows: Query) -> Query:
        """Only works with tables with 'amount' field present"""
        if not hasattr(table, "amount"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ExceptionDescription.RESOURCE_CANNOT_BE_SORTED_BY_AMOUNT.value,
            )

        sorted_by_amount = selected_rows.order_by(table.amount.desc())
        return sorted_by_amount
