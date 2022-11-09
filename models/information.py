from decimal import Decimal

import pydantic
from pydantic import BaseModel

from storage.tables import AccountType


class UserAccountOut(BaseModel):
    user_id: int
    type: AccountType
    balance: pydantic.condecimal(ge=Decimal(0))

    class Config:
        orm_mode = True
