from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from models.information import UserAccountOut
from models.transactions import (
    DepositTransactionOut,
    FundsTransferTransactionOut,
    ReserveTransactionOut,
    ReserveRefundTransactionOut,
    PaymentTransactionOut,
)
from services.information import InformationService


router = APIRouter(prefix="/information", tags=["information"])


# AS: Нейминг: В названии функций здесь и ниже info не содержит доп. смысла
# AS: Нейминг: Вообще лучше, по возможности, не использовать одинаковые названия для разных (хоть и связанных) функций
# AS: Нейминг: Возможно стоит еще разбить url'ы. В духе: account/balance, account/transactions
# AS: Строку длинной в 121 символ не все одобрят. Особенно black.
# AS: Здесь и ниже. Я так понимаю, энергии на комменты к эндпоинтам уже не хватило?
@router.get("/account-balance/{user_id}", response_model=list[UserAccountOut])
def get_account_balance_info(user_id: int, information_service: InformationService = Depends()) -> list[UserAccountOut]:
    return information_service.get_account_balance_info(user_id)


# AS: Под такие длинные аннотации нужно создавать отдельные типы или дженерики
@router.get(
    "/account-transactions/{user_id}",
    response_model=list[
        DepositTransactionOut |
        FundsTransferTransactionOut |
        ReserveTransactionOut |
        ReserveRefundTransactionOut |
        PaymentTransactionOut,
    ],
)
def get_account_transactions_info(
    user_id: int,
    page: int | None = Query(default=None, ge=1),
    sort_by_amount: bool = False,
    sort_by_date: bool = False,
    information_service: InformationService = Depends(),
) -> list[
    DepositTransactionOut |
    FundsTransferTransactionOut |
    ReserveTransactionOut |
    ReserveRefundTransactionOut |
    PaymentTransactionOut
] | JSONResponse:
    return information_service.get_account_transactions_info(
        user_id,
        page=page,
        sort_by_amount=sort_by_amount,
        sort_by_date=sort_by_date,
    )
