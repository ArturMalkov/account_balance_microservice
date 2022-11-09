-- users
INSERT INTO users (first_name, last_name, username, email, phone_number)
VALUES
    ('Guido', 'van Rossum', 'benevolent_dictator', 'guido@python.org', '+4494309127'),
    ('David', 'Beazley', 'async_god', 'beazley@python.org', '+32415793012'),
    ('Yuri', 'Selivanov', 'async_master', 'selivanov@python.org', '+550987184'),
    ('Robert', 'Martin', 'uncle_bob', 'bob@cleancode.org', '+319837430938'),
    ('Raymond', 'Hettinger', 'theremustbeabetterwayman', 'ray@python.org', '+50366758562');


-- company accounts
INSERT INTO company_accounts (balance, bank_account_number, bank)
VALUES
    (0, '38100000048105672', 'Bank of New York Mellon');


-- services
INSERT INTO services (name, price, description)
VALUES
    ('IT support', 30000, 'System administration'),
    ('Legal support', 50000, 'Contracts, litigation, inheritance'),
    ('Catering', 20000, 'Food services for all offsite events'),
    ('Cleaning', 10000, '24/7 cleaning services'),
    ('Medical services', 70000, 'Full range of medical services: dentistry, surgery, etc.'),
    ('Plumbing services', 10000, '24/7 maintenance of private water supply systems');


-- orders
INSERT INTO orders (status, user_id)
VALUES
    ('NOT_SUBMITTED', 1),
    ('NOT_SUBMITTED', 2),
    ('NOT_SUBMITTED', 3),
    ('NOT_SUBMITTED', 4),
    ('NOT_SUBMITTED', 5),
    ('NOT_SUBMITTED', 1),
    ('NOT_SUBMITTED', 2),
    ('NOT_SUBMITTED', 3);


-- order_items
INSERT INTO order_items (quantity, service_id, order_id)
VALUES
    (1, 6, 1),
    (2, 5, 2),
    (3, 4, 3),
    (1, 3, 4),
    (3, 1, 1),
    (1, 2, 3),
    (1, 4, 5),
    (1, 4, 1),
    (1, 1, 2),
    (3, 4, 4),
    (2, 2, 1),
    (1, 1, 3),
    (1, 2, 4),
    (1, 3, 5),
    (2, 5, 1),
    (1, 6, 3),
    (3, 5, 4),
    (2, 1, 8),
    (1, 6, 6),
    (2, 2, 5),
    (1, 3, 7),
    (3, 2, 6);
