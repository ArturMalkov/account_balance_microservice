from enum import Enum


class MessageDescription(str, Enum):
    NO_TRANSACTIONS_AVAILABLE = "no transactions were made on the specified account"
