from enum import Enum


# TODO: think about classification of exceptions
class ExceptionDescription(str, Enum):
    ACCOUNT_BALANCE_CANNOT_BE_NEGATIVE = "User account balance cannot be negative. Transaction failed."
    SENDER_AND_RECIPIENT_CANNOT_BE_THE_SAME_PERSON = "Sender and recipient cannot be the same person."
    ACCOUNT_DOES_NOT_EXIST = "User doesn't have an account yet. Please deposit or transfer money to " \
                             "that user."
    USER_DOES_NOT_EXIST = "Specified user doesn't exist."
    RESOURCE_CANNOT_BE_SORTED_BY_DATE = "Requested resource cannot be sorted by date."
    RESOURCE_CANNOT_BE_SORTED_BY_AMOUNT = "Requested resource cannot be sorted by amount."
    RESULTS_NOT_AVAILABLE_FOR_THIS_PAGE = "Requested page results not found."
    NO_SERVICES_RENDERED_IN_THE_PERIOD = "No services were rendered in the requested period."
    INCORRECT_ORDER_STATUS = "This transaction cannot be performed on this order since it is in " \
                             "'{order_status}' status."
    TRANSACTION_DOES_NOT_EXIST = "Transaction doesn't exist."
    ORDER_DOES_NOT_EXIST = "Specified order does not exist."
    COMPANY_ACCOUNT_DOES_NOT_EXIST = "Specified company account does not exist."
