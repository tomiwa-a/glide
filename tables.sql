BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 40f059c93dfc

CREATE TABLE merchants (
    id SERIAL NOT NULL, 
    name VARCHAR NOT NULL, 
    products INTEGER[], 
    logo VARCHAR, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id)
);

INSERT INTO alembic_version (version_num) VALUES ('40f059c93dfc') RETURNING alembic_version.version_num;

-- Running upgrade 40f059c93dfc -> 6af0df4e45c0

CREATE TABLE main_products (
    id SERIAL NOT NULL, 
    name VARCHAR NOT NULL, 
    PRIMARY KEY (id)
);

INSERT INTO main_products (name) VALUES ('Gas');

INSERT INTO main_products (name) VALUES ('Petrol');

UPDATE alembic_version SET version_num='6af0df4e45c0' WHERE alembic_version.version_num = '40f059c93dfc';

-- Running upgrade 6af0df4e45c0 -> f7c82a3ad1ee

CREATE TABLE merchant_branches (
    id SERIAL NOT NULL, 
    name VARCHAR NOT NULL, 
    merchant_id INTEGER NOT NULL, 
    longitude VARCHAR NOT NULL, 
    lattitude VARCHAR NOT NULL, 
    products INTEGER[] NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(merchant_id) REFERENCES merchants (id) ON DELETE CASCADE
);

UPDATE alembic_version SET version_num='f7c82a3ad1ee' WHERE alembic_version.version_num = '6af0df4e45c0';

-- Running upgrade f7c82a3ad1ee -> 38a5e5d5346c

UPDATE alembic_version SET version_num='38a5e5d5346c' WHERE alembic_version.version_num = 'f7c82a3ad1ee';

-- Running upgrade 38a5e5d5346c -> ea221320f3e6

CREATE TABLE products (
    id SERIAL NOT NULL, 
    branch_id INTEGER NOT NULL, 
    product_id INTEGER NOT NULL, 
    price FLOAT NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(branch_id) REFERENCES merchant_branches (id) ON DELETE CASCADE, 
    FOREIGN KEY(product_id) REFERENCES main_products (id) ON DELETE CASCADE
);

UPDATE alembic_version SET version_num='ea221320f3e6' WHERE alembic_version.version_num = '38a5e5d5346c';

-- Running upgrade ea221320f3e6 -> fed72d123f3f

CREATE TABLE merchant_roles (
    id SERIAL NOT NULL, 
    name VARCHAR NOT NULL, 
    PRIMARY KEY (id)
);

INSERT INTO merchant_roles (name) VALUES ('merchant');

INSERT INTO merchant_roles (name) VALUES ('branch');

INSERT INTO merchant_roles (name) VALUES ('worker');

UPDATE alembic_version SET version_num='fed72d123f3f' WHERE alembic_version.version_num = 'ea221320f3e6';

-- Running upgrade fed72d123f3f -> c694c38469cc

CREATE TABLE merchant_staff (
    id SERIAL NOT NULL, 
    role INTEGER NOT NULL, 
    name VARCHAR, 
    username VARCHAR NOT NULL, 
    password VARCHAR NOT NULL, 
    first_time INTEGER NOT NULL, 
    merchant INTEGER NOT NULL, 
    merchant_branch INTEGER, 
    created_by TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(role) REFERENCES merchant_roles (id) ON DELETE CASCADE, 
    FOREIGN KEY(merchant) REFERENCES merchants (id) ON DELETE CASCADE, 
    FOREIGN KEY(merchant_branch) REFERENCES merchant_branches (id) ON DELETE CASCADE
);

UPDATE alembic_version SET version_num='c694c38469cc' WHERE alembic_version.version_num = 'fed72d123f3f';

-- Running upgrade c694c38469cc -> 7879ec0aa663

CREATE TYPE status AS ENUM ('active', 'disabled', 'pending');

ALTER TABLE merchant_staff ADD COLUMN status status NOT NULL;

ALTER TABLE merchant_branches ADD COLUMN status status NOT NULL;

ALTER TABLE merchants ADD COLUMN status status NOT NULL;

ALTER TABLE products ADD COLUMN status status NOT NULL;

UPDATE alembic_version SET version_num='7879ec0aa663' WHERE alembic_version.version_num = 'c694c38469cc';

-- Running upgrade 7879ec0aa663 -> 7922166fd3a7

CREATE TABLE countries (
    id SERIAL NOT NULL, 
    country VARCHAR NOT NULL, 
    PRIMARY KEY (id)
);

UPDATE alembic_version SET version_num='7922166fd3a7' WHERE alembic_version.version_num = '7879ec0aa663';

-- Running upgrade 7922166fd3a7 -> f3857d126d07

CREATE TABLE states (
    id SERIAL NOT NULL, 
    state VARCHAR NOT NULL, 
    country_id INTEGER, 
    PRIMARY KEY (id), 
    FOREIGN KEY(country_id) REFERENCES countries (id) ON DELETE CASCADE
);

UPDATE alembic_version SET version_num='f3857d126d07' WHERE alembic_version.version_num = '7922166fd3a7';

-- Running upgrade f3857d126d07 -> 898ef5ffe0c9

CREATE TABLE users (
    id SERIAL NOT NULL, 
    first_name VARCHAR NOT NULL, 
    last_name VARCHAR NOT NULL, 
    email VARCHAR NOT NULL, 
    password VARCHAR NOT NULL, 
    phone_number VARCHAR NOT NULL, 
    country INTEGER, 
    state INTEGER, 
    referal INTEGER NOT NULL, 
    dob DATE, 
    address VARCHAR, 
    balance FLOAT, 
    pin INTEGER, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    status status NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (email), 
    FOREIGN KEY(country) REFERENCES countries (id), 
    FOREIGN KEY(state) REFERENCES states (id), 
    UNIQUE (referal)
);

UPDATE alembic_version SET version_num='898ef5ffe0c9' WHERE alembic_version.version_num = 'f3857d126d07';

COMMIT;

