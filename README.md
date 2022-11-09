#Avito Trainee Backend 2022 Task

Project

I just love **black** text

Language: **Python (3.10)**

Web-framework: **FastAPI**

ORM: **SQLAlchemy (async)**

Database: **PostgreSQL**


The project is *done* by me

And this text is ***really important***

Example request:
>curl HTTP /1.1 www.pppp.ru
 
To run database migrations:
> alembic upgrade head


Весь код должен быть выложен на Github с Readme файлом с инструкцией по запуску и примерами запросов/ответов (можно просто описать в Readme методы, можно через Postman, можно в Readme curl запросы скопировать, и так далее).


При возникновении вопросов по ТЗ оставляем принятие решения за кандидатом (в таком случае Readme файле к проекту должен быть указан список вопросов с которыми кандидат столкнулся и каким образом он их решил).

Разработка интерфейса в браузере НЕ ТРЕБУЕТСЯ. Взаимодействие с API предполагается посредством запросов из кода другого сервиса. Для тестирования можно использовать любой удобный инструмент. Например: в терминале через curl или Postman.

URLs:

- information/account-balance/{user_id} or account_id
- information/account-transactions/{user_id} or account_id


- transactions/deposit
- transactions/transfer
- transactions/reserve
- transactions/reserve-refund
- transactions/make-payment


- reports/consolidated/monthly/


**Mechanism**:

<ins>Information part - Balance info/transactions checks</ins>
1. Provide user with account info (balance amount)
2. Provide user with all transactions on his/her regular account

<ins>Functionality - Performing Transactions</ins>
1. Money is deposited (using 3rd party services) to the user account (for the first time) - regular account info is added to the 'accounts' table with the funds deposited
2. Money is deposited (using 3rd party services) to the user account (NOT for the first time) - deposited funds are added to the balance of an existing regular account
3. Order is placed and money is transferred to the reserve account - reserve account info is added to the 'accounts' table (or better create it simultaneously with regular account) with the funds reserved + funds are withdrawn from the regular account
4. Order is cancelled and money is transferred back to the regular account - funds are added to the balance of a regular account and withdrawn from the reserve account
5. Order is delivered and money is transferred to the company account - funds are added to the balance of a company account and withdrawn from the regular account
6. Money transfers between users - funds are added to the balance of a to_user and withdrawn from the balance of a from_user

<ins>Reporting part - Report for Accounting Department</ins>
1. CSV report for 