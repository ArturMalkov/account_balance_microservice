**Avito Backend 2022 Account Balance Microservice Project - Python version**

Link to the task - https://github.com/avito-tech/internship_backend_2022

Technology Stack:
- Programming Language: **Python (3.10)**

- Web-framework: **FastAPI**

- ORM: **SQLAlchemy**

- Database: **PostgreSQL**


**Project Description**:

<ins>Information service - Balances/transactions info</ins>
- Provides user with his/her accounts' (both reserve and regular) info (including balance amount)

Example request:
>curl HTTP /1.1 www.pppp.ru

Example response:
>curl HTTP /1.1 www.pppp.ru

- Provides user with info on all transactions on his/her accounts (both reserve and regular) - a list of transactions with description on where and why the funds were credited/debited from the account balance is provided. Sorting (by date and amount) and pagination of results are provided as an option.

<ins>Transaction service - Transactions functionality</ins>
- Money is deposited (using 3rd party services) to the user regular account (*for the first time*) - regular account info is added to the 'user_accounts' table with the funds deposited (reserve account info is added to the 'user_accounts' table as well)
*OR*
Money is deposited (using 3rd party services) to the user regular account (*NOT for the first time*) - deposited funds are added to the balance of an existing regular account
- Money transfers between users - funds are added to the balance of a to_user and withdrawn from the balance of a from_user
- Order is placed and money is transferred from user's regular account to the reserve one 
- Order is cancelled and money is transferred back from user's reserve account to the regular one
- Order is delivered and money is transferred from user's reserve account to the company account

<ins>Report service - Reports functionality</ins>
- Provides .csv report with total revenues for each service rendered in the requested period. 


**OpenAPI documentation (with Swagger UI and more detailed description of API)**:
>'/docs'

 
**To run the containers**:
> docker-compose up --build
