CREATE TABLE stock (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE stock_price (
    stock_id INTEGET NOT NULL,
    dt TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    bid NUMERIC NOT NULL,
    ask NUMERIC NOT NULL,
    ltp NUMERIC NOT NULL,
    ltv NUMERIC NOT NULL,
    PRIMARY KEY (stock_id, dt)
    CONSTRAINT fk_stock FOREIGN KEY (stock_id) REFERENCES stock (id)
);

CREATE INDEX ON stock_price (stock_id, dt DESC);

SELECT create_hypertable('stock_price', 'dt');