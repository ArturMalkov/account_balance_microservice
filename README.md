**Avito Backend 2022 Account Balance Microservice Project - Python version**:metal:


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
    >curl -X 'GET' \
      'http://127.0.0.1:8000/v1/information/account-balance/2' \
      -H 'accept: application/json'
    
    Example response body:
    >[
        {
            "user_id": 2,
            "type": "regular",
            "balance": 199.99
         },
        {
            "user_id": 2,
            "type": "reserve",
            "balance": 0
        }
      ]

- Provides user with info on all transactions on his/her accounts (both reserve and regular) - a list of transactions with description on where and why the funds were credited/debited from the account balance is provided. Sorting (by date and amount) and pagination of results are provided as an option

    Example request:
    >curl -X 'GET' \
        'http://127.0.0.1:8000/v1/information/account-transactions/2?page=1&sort_by_amount=true&sort_by_date=false' \
        -H 'accept: application/json'
    
    Example response body:
    >[
        {
            "description": "Money in the amount of 100000000USD was deposited to user 2 from external services on 2022-11-17 01:44:22.083065.",
            "date": "2022-11-17T01:44:22.083065",
            "amount": 100000000,
            "type": "deposit",
            "to_user_id": 2
        },
        {
            "description": "Money in the amount of 170000USD was reserved on user 2 reserve account as per the order 2 on 2022-11-17 01:44:28.512439.",
            "date": "2022-11-17T01:44:28.513439",
            "amount": 170000,
            "type": "reserve",
            "order_id": 2
        },
        {
            "description": "Money in the amount of 170000USD was refunded to user 2 account from his/her reserve account as per the order 2 on 2022-11-17 01:46:55.031078.",
            "date": "2022-11-17T01:46:55.032078",
            "amount": 170000,
            "type": "reserve refund",
            "order_id": 2
        },
        {
            "description": "Money in the amount of 500USD was transferred from user 1 to user 2 on 2022-11-17 01:37:52.240125.",
            "date": "2022-11-17T01:37:52.240125",
            "amount": 500,
            "type": "funds transfer",
            "to_user_id": 2
        },
        {
            "description": "Money in the amount of 199.99USD was deposited to user 2 from external services on 2022-11-17 01:26:25.982780.",
            "date": "2022-11-17T01:26:25.984779",
            "amount": 199.99,
            "type": "deposit",
            "to_user_id": 2
        }
    ]

<ins>Transaction service - Transactions functionality</ins>
- Money is deposited (using 3rd party services) to the user regular account (*for the first time*) - regular account info is added to the 'user_accounts' table with the funds deposited (reserve account info is added to the 'user_accounts' table as well)
*OR*
Money is deposited (using 3rd party services) to the user regular account (*NOT for the first time*) - deposited funds are added to the balance of an existing regular account

    Example request:
    >curl -X 'PATCH' \
      'http://127.0.0.1:8000/v1/transactions/deposit' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "type": "deposit",
      "amount": 199.99,
      "to_user_id": 2
       }'
    
    Example response body:
    >{
        "description": "Money in the amount of 199.99USD was deposited to user 2 from external services on 2022-11-17 01:40:55.779889.",
        "date": "2022-11-17T01:40:55.780889",
        "amount": 199.99,
        "type": "deposit",
        "to_user_id": 2
     }

- Money transfers between users - funds are added to the balance of a to_user and withdrawn from the balance of a from_user

    Example request:
    >curl -X 'PATCH' \
        'http://127.0.0.1:8000/v1/transactions/transfer' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
        "type": "funds transfer",
        "amount": 500,
        "from_user_id": 1,
        "to_user_id": 2
         }'
    
    Example response body:
    >{
        "description": "Money in the amount of 500USD was transferred from user 1 to user 2 on 2022-11-17 01:37:52.240125.",
        "date": "2022-11-17T01:37:52.240125",
        "amount": 500,
        "type": "funds transfer",
        "from_user_id": 1,
        "to_user_id": 2
     }

- Order is placed and money is transferred from user's regular account to the reserve one 

    Example request:
    >curl -X 'PATCH' \
        'http://127.0.0.1:8000/v1/transactions/reserve' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
        "type": "reserve",
        "order_id": 2
        }'
    
    Example response body:
    >{
        "description": "Money in the amount of 170000USD was reserved on user 2 reserve account as per the order 2 on 2022-11-17 01:44:28.512439.",
        "date": "2022-11-17T01:44:28.513439",
        "amount": 170000,
        "type": "reserve",
        "order_id": 2
     }

- Order is cancelled and money is transferred back from user's reserve account to the regular one

    Example request:
    >curl -X 'PATCH' \
        'http://127.0.0.1:8000/v1/transactions/reserve-refund' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
        "type": "reserve refund",
        "order_id": 2
        }'
    
    Example response body:
    >{
        "description": "Money in the amount of 170000USD was refunded to user 2 account from his/her reserve account as per the order 2 on 2022-11-17 01:46:55.031078.",
        "date": "2022-11-17T01:46:55.032078",
        "amount": 170000,
        "type": "reserve refund",
        "order_id": 2
     }

- Order is delivered and money is transferred from user's reserve account to the company account

    Example request:
    >curl -X 'PATCH' \
        'http://127.0.0.1:8000/v1/transactions/make-payment' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
        "type": "payment to company",
        "order_id": 1,
        "to_company_account": 1
        }'
    
    Example response body:
    >{
        "description": "Money in the amount of 350000USD was paid by user 1 to the company account as per the order 1 on 2022-11-17 01:49:56.228794.",
        "date": "2022-11-17T01:49:56.232796",
        "amount": 350000,
        "type": "payment to company",
        "order_id": 1,
        "to_company_account": 1
    }
    
<ins>Report service - Reports functionality</ins>
- Provides .csv report with total revenues for each service rendered in the requested period. 

    Example request:
    >curl -X 'GET' \
        'http://127.0.0.1:8000/v1/reports/consolidated/monthly?year=2022&month=11' \
        -H 'accept: application/json'
          
    Example response headers:
    > content-disposition: attachment; filename=report_2022-11.csv 
      content-type: text/csv; charset=utf-8 
      date: Thu,17 Nov 2022 01:55:08 GMT 
      server: uvicorn 
      transfer-encoding: chunked 


**OpenAPI documentation (with Swagger UI and more detailed description of API)**:
>'/docs'

 
**To run the containers**:
> docker compose up --build

**To fill the database with test data, use**:
> /scripts/database_populate.sql
