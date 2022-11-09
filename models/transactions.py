import datetime
from decimal import Decimal

import pydantic
from pydantic import BaseModel

from exceptions import ExceptionDescription
from storage.tables import TransactionType


class CompanyAccount(BaseModel):
    balance: pydantic.condecimal(ge=Decimal(0))

    class Config:
        orm_mode = True


class BaseTransactionIn(BaseModel):
    pass


class DepositTransactionIn(BaseTransactionIn):
    type: TransactionType = TransactionType.DEPOSIT
    amount: pydantic.condecimal(gt=Decimal(0))
    to_user_id: int


class FundsTransferTransactionIn(BaseTransactionIn):
    type: TransactionType = TransactionType.FUNDS_TRANSFER
    amount: pydantic.condecimal(gt=Decimal(0))
    from_user_id: int
    to_user_id: int

    @pydantic.root_validator
    @classmethod
    def check_that_sender_and_recipient_are_not_the_same_person(cls, values):
        if values.get("from_user_id") == values.get("to_user_id"):
            raise ValueError(ExceptionDescription.SENDER_AND_RECIPIENT_CANNOT_BE_THE_SAME_PERSON.value)

        return values


class ReserveTransactionIn(BaseTransactionIn):
    type: TransactionType = TransactionType.RESERVE
    order_id: int


class ReserveRefundTransactionIn(BaseTransactionIn):
    type: TransactionType = TransactionType.RESERVE_REFUND
    order_id: int


class PaymentTransactionIn(BaseTransactionIn):
    type: TransactionType = TransactionType.PAYMENT_TO_COMPANY
    order_id: int
    to_company_account: int = 1  # while the company may potentially have multiple bank accounts, for the purposes
    # of this project it only has one account and all payments are made to that account by default.


class BaseTransactionOut(BaseModel):
    description: str
    date: datetime.datetime
    amount: Decimal

    class Config:
        orm_mode = True


class DepositTransactionOut(DepositTransactionIn, BaseTransactionOut):
    pass


class FundsTransferTransactionOut(FundsTransferTransactionIn, BaseTransactionOut):
    pass


class ReserveTransactionOut(ReserveTransactionIn, BaseTransactionOut):
    pass


class ReserveRefundTransactionOut(ReserveRefundTransactionIn, BaseTransactionOut):
    pass


class PaymentTransactionOut(PaymentTransactionIn, BaseTransactionOut):
    pass
