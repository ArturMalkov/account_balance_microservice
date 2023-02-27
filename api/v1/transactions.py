from fastapi import (
    APIRouter,
    Depends,
)

from models.transactions import (
    DepositTransactionIn,
    DepositTransactionOut,
    FundsTransferTransactionIn,
    FundsTransferTransactionOut,
    ReserveTransactionIn,
    ReserveTransactionOut,
    ReserveRefundTransactionIn,
    ReserveRefundTransactionOut,
    PaymentTransactionIn,
    PaymentTransactionOut,
)
from services.transactions import TransactionsService


router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)


# AS: Тут создается транзакция и делается апдейт баланса получателя (к балансу на аккаунте отдельные комменты)
# AS: Как по мне это точно POST, а не PATCH (тем более, что это все происходит в домене Транзакции).
@router.patch("/deposit", response_model=DepositTransactionOut)
def deposit_funds_to_account(
    transaction_data: DepositTransactionIn,
    transactions_service: TransactionsService = Depends(),
) -> DepositTransactionOut:
    """
    Deposits a specified amount of money to a specific user (i.e. user account balance increases) via external services
    (which are out of scope for this project).
    If user doesn't have an account yet, account will be created (as per the project's requirements)
    and money will be deposited to the account.
    """
    return transactions_service.deposit_funds_to_account(transaction_data)


# AS: Аналогично, для меня это POST.
# AS: Так как переводы бывают людям и компаниям, то я бы их группировал по такому признаку в духе:
# AS: "/transfer/c2c", "/transfer/c2b", etc
@router.patch("/transfer", response_model=FundsTransferTransactionOut)
def transfer_funds_between_user_accounts(
    transaction_data: FundsTransferTransactionIn,
    transactions_service: TransactionsService = Depends(),
) -> FundsTransferTransactionOut:
    """
    Transfers a specified amount of money from one user to another (i.e. sender account balance decreases while
    recipient account balance increases accordingly).
    If a recipient user doesn't have an account yet, account will be created (as per the project's requirements)
    and money will be transferred to the account.
    """
    return transactions_service.transfer_funds_between_user_accounts(transaction_data)


@router.patch("/reserve", response_model=ReserveTransactionOut)
def reserve_funds(
    transaction_data: ReserveTransactionIn,
    transactions_service: TransactionsService = Depends(),
) -> ReserveTransactionOut:
    """
    Reserves money from account of a user which made a specific order (money is transferred from user's regular account
    to reserve one).
    Changes the order's status to "in progress".
    Reserved money can later be refunded to regular account (if the order is cancelled)
    or paid to the company (if the order is fulfilled).
    The amount of money to be reserved is determined by the total price of the services in the order.
    """
    return transactions_service.reserve_funds(transaction_data)


# AS: Вопрос к имени пути и имени функции. Немного неоднородно и сбивает с мысли.
@router.patch("/reserve-refund", response_model=ReserveRefundTransactionOut)
def cancel_reserve(
    transaction_data: ReserveRefundTransactionIn,
    transactions_service: TransactionsService = Depends(),
) -> ReserveRefundTransactionOut:
    """
    Refunds previously reserved money (money is transferred back from user's reserve account to regular one) as per
    specific order.
    Changes the order's status to "cancelled".
    """
    return transactions_service.cancel_reserve(transaction_data)


# AS: Аналогично, для меня это POST.
# AS: Так как переводы бывают людям и компаниям, то я бы их группировал по такому признаку в духе:
# AS: "/transfer/c2c", "/transfer/c2b", etc
@router.patch("/make-payment", response_model=PaymentTransactionOut)
def make_payment_to_company(
    transaction_data: PaymentTransactionIn,
    transactions_service: TransactionsService = Depends(),
) -> PaymentTransactionOut:
    """
    Transfers previously reserved money to company account (money is transferred from user's reserve account to
    company account).
    Changes the order's status to "completed".
    """
    return transactions_service.make_payment_to_company(transaction_data)
