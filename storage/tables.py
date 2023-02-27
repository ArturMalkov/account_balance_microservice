import datetime
from enum import Enum

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM as pgEnum
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.types import DECIMAL

from storage.database import engine


Base = declarative_base()


# AS: Здесь и далее. Я использую стандарт нейминга сущностей БД.
# AS: https://www.isbe.net/documents/sql_server_standards.pdf 
# AS: Хотя, как я понимаю, питонисты, которые работают через ORM забивают на такие вещи.
class User(Base):
    __tablename__ = "users"

    # AS: Здесь и далее. У столбцов отсутствуют аннотации.
    id = sa.Column(sa.Integer, primary_key=True)
    first_name = sa.Column(sa.String(50))
    last_name = sa.Column(sa.String(50))
    username = sa.Column(sa.String(50), unique=True, nullable=False)
    email = sa.Column(sa.String(50), unique=True, nullable=False)
    phone_number = sa.Column(sa.String(50), unique=True, nullable=False)

    # AS: Здесь и далее. У relationship'ов отсутствуют аннотации. IDE не одобряет.
    accounts = relationship("UserAccount", backref="user", cascade="all, delete")
    orders = relationship("Order", backref="user", cascade="all, delete")

    def __repr__(self):
        # AS: Здесь и далее. Очень длинный repr. Для отладки такой не нужен. И даже если вдруг нужен, то лучше использовать reprlib.
        return (
            f"<{self.__class__.__name__} id={self.id} first_name={self.first_name} last_name={self.last_name}"
            f"username={self.username} email={self.email} phone_number={self.phone_number}>"
        )


# AS: Я бы сложил все Enum'ы в отдельный файл и не мешал их в один файл с таблицами
class AccountType(str, Enum):
    REGULAR = "regular"
    RESERVE = "reserve"


class UserAccount(Base):
    __tablename__ = "user_accounts"

    id = sa.Column(sa.Integer, primary_key=True)
    # AS: Сам грешу тем же, но называть стобец type - плохо. Потом штуки типа type(User.type) разгребать.
    type = sa.Column(pgEnum(AccountType), nullable=False)
    # AS: Тут один из самых важных архитектурных вопросов для меня. Должен ли у аккаунта хранится баланс?
    # AS: Мой ответ одназначный - нет, не должен. И насколько я знаю почти никто его не хранит в таком виде.
    # AS: Тут можно рассуждать, но риски неконсистентности высокие. Бэст прэктиз - собирать динамически.
    balance = sa.Column(DECIMAL, default=0)
    # AS: Здесь и далее. Если есть foreign key, то логично и relationship делать.
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), index=True)

    def __repr__(self):
        return f"<{self.__class__.__name__} type={self.type} balance={self.balance} user_id={self.user_id}>"


class CompanyAccount(Base):
    __tablename__ = "company_accounts"

    id = sa.Column(sa.Integer, primary_key=True)
    balance = sa.Column(DECIMAL, default=0)
    bank_account_number = sa.Column(sa.String(50), nullable=False)
    bank = sa.Column(sa.String(50), nullable=False)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} balance={self.balance} bank_account_number={self.bank_account_number}"
            f"bank={self.bank}>"
        )


class OrderStatus(str, Enum):
    # AS: Злесь и далее. Я бы не использовал значения с пробелами
    NOT_SUBMITTED = "not submitted"
    IN_PROGRESS = "in progress"  # money can be transferred from regular account to reserve account (of the same user)
    COMPLETED = "completed"  # money can be withdrawn from reserve account and credited to company account
    CANCELLED = "cancelled"  # money can be returned from reserve account to regular account (of the same user)


class Order(Base):
    __tablename__ = "orders"

    id = sa.Column(sa.Integer, primary_key=True)
    status = sa.Column(pgEnum(OrderStatus), default=OrderStatus.NOT_SUBMITTED)
    # AS: Почему тут на 3 строки разъехалось?
    user_id = sa.Column(
        sa.Integer, sa.ForeignKey("users.id"), index=True
    )

    items = relationship("OrderItem", backref="order", cascade="all, delete")
    transactions = relationship("Transaction", backref="order")

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id} status={self.status} user_id={self.user_id}>"


class OrderItem(Base):
    """Represents a service added to the order"""

    __tablename__ = "order_items"

    id = sa.Column(sa.Integer, primary_key=True)
    quantity = sa.Column(sa.Integer, default=1)
    service_id = sa.Column(sa.Integer, sa.ForeignKey("services.id"), index=True)
    order_id = sa.Column(sa.Integer, sa.ForeignKey("orders.id"), index=True)

    # AS: Почему тут unique constrains в table args, если сверху (например в User) они были просто в колонках?
    __table_args__ = (
        sa.UniqueConstraint('service_id', 'order_id'),
        sa.CheckConstraint('quantity > 0'),
    )

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} service_id={self.service_id} quantity={self.quantity} "
            f"order_id={self.order_id}>"
        )


class Service(Base):
    __tablename__ = "services"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50), nullable=False)
    price = sa.Column(DECIMAL, nullable=False)
    description = sa.Column(sa.String(255), nullable=False)

    ordered_services = relationship("OrderItem", backref="service", cascade="all, delete")

    __table_args__ = (
        sa.CheckConstraint('price >= 0'),
        # == 0 - let's assume that in some cases service can cost 0 (as part of clients incentive program)
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name} price={self.price} description={self.description}>"


class TransactionType(str, Enum):
    DEPOSIT = "deposit"  # ... (external service) -> regular account
    FUNDS_TRANSFER = "funds transfer"  # regular account -> regular account
    RESERVE = "reserve"  # regular -> reserve accounts of the same user
    RESERVE_REFUND = "reserve refund"  # reserve -> regular accounts of the same user
    PAYMENT_TO_COMPANY = "payment to company"  # reserve account -> company account


class Transaction(Base):
    __tablename__ = "transactions"

    id = sa.Column(sa.Integer, primary_key=True)
    amount = sa.Column(DECIMAL)
    type = sa.Column(pgEnum(TransactionType), nullable=False)
    description = sa.Column(sa.String(255), nullable=False)
    # AS: Тут я бы сделал более точный нейминг. Дата чего? Дата создания. Еще, например, может быть дата изменения.
    date = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    # AS: Вопрос по nullable, но это уже тонкости реализации
    order_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("orders.id"),
        default=None,
        index=True,
        nullable=True,
    )
    from_user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), default=None, nullable=True)
    to_user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), default=None, nullable=True)
    to_company_account = sa.Column(
        sa.Integer,
        sa.ForeignKey("company_accounts.id"),
        default=None,
        nullable=True,
    )

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} amount={self.amount} type={self.type} description={self.description} "
            f"date={self.date} order_id={self.order_id} from_user_id={self.from_user_id} to_user_id={self.to_user_id}"
            f"to_company_account={self.to_company_account}>"
        )


Base.metadata.create_all(engine)  # TODO: to substitute with migrations
