**Avito Backend 2022 Account Balance Microservice Project - Python version**

Link to the task - https://github.com/avito-tech/internship_backend_2022

Technology Stack:
- Programming Language: **Python (3.10)**

- Web-framework: **FastAPI**

- ORM: **SQLAlchemy**

- Database: **PostgreSQL**


**Project Description**:

<ins>Information service - Balances/transactions info</ins>
1. Provide user with his/her accounts' (both reserve and regular) info (including balance amount)
2. Provide user with info on all transactions on his/her accounts (both reserve and regular)

<ins>Transaction service - Performing Transactions</ins>
1. Money is deposited (using 3rd party services) to the user regular account (*for the first time*) - regular account info is added to the 'user_accounts' table with the funds deposited (reserve account info is added to the 'user_accounts' table as well)
OR
Money is deposited (using 3rd party services) to the user regular account (*NOT for the first time*) - deposited funds are added to the balance of an existing regular account
2. Order is placed and money is transferred to the reserve account - reserve account info is added to the 'accounts' table (or better create it simultaneously with regular account) with the funds reserved + funds are withdrawn from the regular account
3. Order is cancelled and money is transferred back to the regular account - funds are added to the balance of a regular account and withdrawn from the reserve account
4. Order is delivered and money is transferred to the company account - funds are added to the balance of a company account and withdrawn from the regular account
5. Money transfers between users - funds are added to the balance of a to_user and withdrawn from the balance of a from_user

<ins>Reporting service - Report for Accounting Department</ins>
1. CSV report for 

Example requests:
>curl HTTP /1.1 www.pppp.ru
 
To run database migrations:
> alembic upgrade head


URLs:

- information/account-balance/{user_id} or account_id
- information/account-transactions/{user_id} or account_id


- transactions/deposit
- transactions/transfer
- transactions/reserve
- transactions/reserve-refund
- transactions/make-payment


- reports/consolidated/monthly/

