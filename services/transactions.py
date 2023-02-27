from datetime import datetime
from decimal import Decimal
from enum import Enum

import sqlalchemy as sa
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from exceptions import ExceptionDescription
from models.transactions import (
    BaseTransactionIn,
    DepositTransactionIn,
    FundsTransferTransactionIn,
    ReserveTransactionIn,
    ReserveRefundTransactionIn,
    PaymentTransactionIn,
)
from services.information import InformationService
from storage import tables
from storage.database import get_db_session
from storage.tables import AccountType, OrderStatus, TransactionType


class TransactionDescription(str, Enum):
    # AS: Это поле в ТЗ есть? Вопрос нужно ли это в БД хранить в таком виде?
    # AS: Второй вопрос нужен ли Enum под это дело и не переместить ли все это дело туда, где оно используется в виде dict'а?
    DEPOSIT = "Money in the amount of {amount}USD was deposited to user {to_user_id} from external services on {date}."
    FUNDS_TRANSFER = (
        "Money in the amount of {amount}USD was transferred from user {from_user_id} to user {to_user_id} on {date}."
    )
    RESERVE = (
        "Money in the amount of {amount}USD was reserved on user {user_id} reserve account as per the order {order_id} "
        "on {date}."
    )
    RESERVE_REFUND = (
        "Money in the amount of {amount}USD was refunded to user {user_id} account from his/her reserve account as "
        "per the order {order_id} on {date}."
    )
    PAYMENT_TO_COMPANY = (
        "Money in the amount of {amount}USD was paid by user {user_id} to the company account as per the "
        "order {order_id} on {date}."
    )


class TransactionsService:
    """Responsible for working with transactions' and accounts' data"""

    def __init__(
        self,
        db_session: Session = Depends(get_db_session),
        information_service: InformationService = Depends(),
    ) -> None:
        self.db_session = db_session
        self.information_service = information_service

    def deposit_funds_to_account(self, transaction_data: DepositTransactionIn) -> tables.Transaction:
        recipient_account = self._get_or_create_recipient_account_by_user_id(transaction_data.to_user_id)

        # AS: Здесь и ниже: Не берусь критиковать подход, но читается трудновато. 
        # AS: Особенно то, что нужен отдельный блок prepare db record.
        # AS: Я бы разбивал на более мелкие кубики. В духе:
        # AS: 1. sender.send_funds(amount)
        # AS: 2. recipient.receive_funds(amount)
        self._transfer_funds(
            sender_account=None,
            recipient_account=recipient_account,
            transfer_amount=transaction_data.amount,
        )

        transaction = self._prepare_transaction_db_record(
            transaction_data,
            TransactionType.DEPOSIT,
            transaction_data.amount,
            to_user_id=transaction_data.to_user_id,
        )

        # AS: Я бы здесь делал только commit(), а add'ы вынес во вложенные методы.
        self.db_session.add_all([recipient_account, transaction])
        self.db_session.commit()

        return transaction

    def transfer_funds_between_user_accounts(self, transaction_data: FundsTransferTransactionIn) -> tables.Transaction:
        """
        Transfers funds between regular(!) accounts of two users.
        """
        sender_account = self.information_service._get_user_account_by_user_id(
            transaction_data.from_user_id, AccountType.REGULAR
        )
        recipient_account = self._get_or_create_recipient_account_by_user_id(transaction_data.to_user_id)

        self._transfer_funds(sender_account, recipient_account, transaction_data.amount)

        transaction = self._prepare_transaction_db_record(
            transaction_data,
            TransactionType.FUNDS_TRANSFER,
            transaction_data.amount,
            transaction_data.from_user_id,
            transaction_data.to_user_id,
        )

        self.db_session.add_all([sender_account, recipient_account, transaction])
        self.db_session.commit()

        return transaction

    def reserve_funds(self, transaction_data: ReserveTransactionIn) -> tables.Transaction:
        # AS: Название метода в 61 символ это сильно
        self._raise_error_if_order_does_not_exist_or_has_irrelevant_status(
            transaction_data.order_id,
            OrderStatus.NOT_SUBMITTED,
        )

        # AS: Здесь и ниже: Выглядит плохо. 
        # AS: И с аннотациями тоже не бьется. Возвращается лист, а присваивается tuple.
        # AS: Во вложенной функции get_users нет сортировки, поэтому порядок может быть любой. Возможен баг.
        (
            regular_account,
            reserve_account,
        ) = self.information_service._get_user_accounts_by_order_id(transaction_data.order_id)

        transaction_amount = self._calculate_transaction_amount(transaction_data.order_id)

        self._transfer_funds(
            sender_account=regular_account,
            recipient_account=reserve_account,
            transfer_amount=transaction_amount,
        )

        transaction = self._prepare_transaction_db_record(
            transaction_data,
            TransactionType.RESERVE,
            transaction_amount,
            regular_account.user_id,
            order_id=transaction_data.order_id,
        )

        self.db_session.add_all([regular_account, reserve_account, transaction])
        _update_order_status(
            order_id=transaction_data.order_id,
            new_status=OrderStatus.IN_PROGRESS,
            db_session=self.db_session,
        )
        self.db_session.commit()

        return transaction

    def cancel_reserve(self, transaction_data: ReserveRefundTransactionIn) -> tables.Transaction:
        self._raise_error_if_order_does_not_exist_or_has_irrelevant_status(
            transaction_data.order_id,
            OrderStatus.IN_PROGRESS,
        )

        reserve_transaction_to_be_cancelled = self._get_transaction_by_order_id(
            transaction_data.order_id, TransactionType.RESERVE
        )

        transaction_amount = reserve_transaction_to_be_cancelled.amount
        (
            regular_account,
            reserve_account,
        ) = self.information_service._get_user_accounts_by_order_id(transaction_data.order_id)

        self._transfer_funds(
            sender_account=reserve_account,
            recipient_account=regular_account,
            transfer_amount=transaction_amount,
        )

        transaction = self._prepare_transaction_db_record(
            transaction_data,
            TransactionType.RESERVE_REFUND,
            transaction_amount,
            regular_account.user_id,
            order_id=transaction_data.order_id,
        )

        self.db_session.add_all([reserve_account, regular_account, transaction])
        _update_order_status(
            order_id=transaction_data.order_id,
            new_status=OrderStatus.CANCELLED,
            db_session=self.db_session,
        )
        self.db_session.commit()

        return transaction

    def make_payment_to_company(self, transaction_data: PaymentTransactionIn) -> tables.Transaction:
        """
        Transfers reserved (as per specified order) money from user's reserve account to company account.
        While the company can potentially have multiple bank accounts, for the purposes of this project it only has one
        account and all payments are made to that account by default.
        """
        self._raise_error_if_order_does_not_exist_or_has_irrelevant_status(
            transaction_data.order_id,
            OrderStatus.IN_PROGRESS,
        )

        reserve_transaction_to_be_paid = self._get_transaction_by_order_id(
            transaction_data.order_id, TransactionType.RESERVE
        )
        transaction_amount = reserve_transaction_to_be_paid.amount
        (
            _,
            reserve_account,
        ) = self.information_service._get_user_accounts_by_order_id(transaction_data.order_id)
        company_account = self.information_service._get_company_account_by_company_account_id(transaction_data.to_company_account)

        self._transfer_funds(
            sender_account=reserve_account,
            recipient_account=company_account,
            transfer_amount=transaction_amount,  # TODO: why float here???
        )

        transaction = self._prepare_transaction_db_record(
            transaction_data,
            TransactionType.PAYMENT_TO_COMPANY,
            transaction_amount,
            reserve_account.user_id,
            order_id=transaction_data.order_id,
        )

        self.db_session.add_all([reserve_account, company_account, transaction])
        _update_order_status(
            order_id=transaction_data.order_id,
            new_status=OrderStatus.COMPLETED,
            db_session=self.db_session,
        )
        self.db_session.commit()

        return transaction

    def _calculate_transaction_amount(self, order_id: int) -> Decimal:
        # AS: Зачем так сложно? Если по id надо, то можно get использовать вместо filter.
        # AS: Нет аннотации тут, и в результате, и ниже их тоже нет. 
        order = self.db_session.query(tables.Order).filter(tables.Order.id == order_id).first()
        # AS: Можно как-то поэлегнтнее посчитать. Вроде:
        # AS: sum([item.quantity * item.service.price] for item in order.items)
        transaction_amount = Decimal(0)

        for ordered_service in order.items:
            transaction_amount += ordered_service.quantity * ordered_service.service.price

        return transaction_amount

    def _get_transaction_by_order_id(self, order_id: int, type_: TransactionType) -> tables.Transaction:
        # AS: Это эксперементы? .all() - это, конечно, сильно.
        # AS: Если я правильно понял логику (не факт), то сначала нужен Order, а от него через relationship забрать транзакции.
        transactions = self.db_session.query(tables.Transaction).all()
        transaction = [transaction for transaction in transactions if transaction.order_id == order_id
                       and transaction.type == type_][0]

        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=ExceptionDescription.TRANSACTION_DOES_NOT_EXIST.value)

        return transaction

    @staticmethod
    def _transfer_funds(
        sender_account: tables.UserAccount | None,
        recipient_account: tables.UserAccount | tables.CompanyAccount,
        transfer_amount: Decimal,
    ) -> None:
        """
        Utility method used to transfer funds in all transactions except for deposits.
        Do not confuse it with transfer_funds_between_user_accounts().
        """
        if sender_account:  # there's no sender account in deposit transaction
            sender_account.balance -= transfer_amount
            if sender_account.balance < 0:
                raise ValueError(ExceptionDescription.ACCOUNT_BALANCE_CANNOT_BE_NEGATIVE.value)
        recipient_account.balance += transfer_amount  # TODO: place logging here???
        # AS: Опционально: Подумать о том, чтобы self.db.session.add() был тут. Это как будто логичнее.
        # AS: Заодно метод перестанет быть static.

    def _get_or_create_recipient_account_by_user_id(
        self,
        user_id: int,
    ) -> tables.UserAccount:
        """
        In case of deposit/money transfer transactions, if a recipient user doesn't have an account yet,
        both regular and reserve accounts will be automatically created with zero balance.
        """
        # AS: Тут не до конца понимаю как это работает с точки зрения бизнес-логики.
        # AS: Если нет user'а, то exception (точно?), но если есть user, но у него аккаунта, то его создавать?
        # AS: А не проще сразу создавать user'а с аккаунтами? Или тут какие-то спец требования есть?
        self.information_service._raise_error_if_user_does_not_exist(user_id)

        # AS: Ну, тут как обычно, я бы делал все на релейшеншипах, но чисто вопрос выбранного подхода.
        regular_account = (
            self.db_session.query(tables.UserAccount)
            .filter(
                sa.and_(
                    tables.UserAccount.user_id == user_id,
                    tables.UserAccount.type == AccountType.REGULAR,
                )
            )
            .first()
        )

        if not regular_account:
            regular_account = tables.UserAccount(user_id=user_id, type=AccountType.REGULAR)
            reserve_account = tables.UserAccount(user_id=user_id, type=AccountType.RESERVE)
            self.db_session.add_all([regular_account, reserve_account])
            self.db_session.commit()

        return regular_account

    def _prepare_transaction_db_record(
        self,
        transaction_data: BaseTransactionIn,
        type_: TransactionType,
        amount: Decimal,
        from_user_id: int | None = None,
        to_user_id: int | None = None,
        order_id: int | None = None,
    ) -> tables.Transaction:
        transaction = tables.Transaction(
            **transaction_data.dict(exclude={"type", "amount"}),
            type=type_,
            amount=amount,
            description=self._prepare_transaction_description(type_, amount, from_user_id, to_user_id, order_id)
        )

        return transaction

    @staticmethod
    def _prepare_transaction_description(
        transaction_type: TransactionType,
        amount: Decimal,
        from_user_id: int | None = None,
        to_user_id: int | None = None,
        order_id: int | None = None,
    ) -> TransactionDescription:
        description_template = TransactionDescription[f"{transaction_type.name}"].value
        date = datetime.utcnow()

        # AS: Для сейчас pattern matching для таких кейсов использую
        if transaction_type == TransactionType.DEPOSIT:
            transaction_description = description_template.format(amount=amount, to_user_id=to_user_id, date=date)
        elif transaction_type == TransactionType.FUNDS_TRANSFER:
            transaction_description = description_template.format(
                amount=amount, from_user_id=from_user_id, to_user_id=to_user_id, date=date
            )
        # AS: Некрасиво
        elif transaction_type in [
            TransactionType.RESERVE,
            TransactionType.RESERVE_REFUND,
            TransactionType.PAYMENT_TO_COMPANY,
        ]:
            transaction_description = description_template.format(
                amount=amount,
                user_id=from_user_id,
                order_id=order_id,
                date=date,
            )

        return transaction_description

    def _raise_error_if_order_does_not_exist_or_has_irrelevant_status(
        self, order_id: int, correct_status: OrderStatus
    ) -> None:
        """
        Helps to avoid situations when order doesn't exist or has irrelevant status with regard to the transaction
        to be performed.
        E.g.:
         for 'reserve' transaction to happen, order must be in 'not submitted' state;
         for 'reserve refund' or 'payment to company' transaction to happen, order must be in 'in progress' state.
        """
        # AS: Зачем так сложно? Если по id надо, то можно get использовать вместо filter.
        order = self.db_session.query(tables.Order).filter(tables.Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=ExceptionDescription.ORDER_DOES_NOT_EXIST.value)

        if order.status != correct_status:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=ExceptionDescription.INCORRECT_ORDER_STATUS.value
                                .format(order_status=order.status))


def _update_order_status(*, order_id: int, new_status: OrderStatus, db_session: Session) -> None:
    """
    This method should belong to another microservice - orders microservice.
    Placed here for demonstration/convenience purposes.
    """
    order = db_session.query(tables.Order).filter(tables.Order.id == order_id).first()
    order.status = new_status

    db_session.add(order)
    # no commit here - commits happen in the methods of the TransactionsService
    # (account balance operations, transactions' saves and order status updates all need to happen within the same
    # transaction)
