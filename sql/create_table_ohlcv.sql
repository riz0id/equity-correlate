CREATE TABLE IF NOT EXISTS ohlcv(
    -- UNIX epoch timestamp in miliseconds.
    t INTEGER NOT NULL,
    -- The ticker for the OHLCV record.
    s TEXT NOT NULL,
    -- The opening price of the asset across the aggregation period.
    o REAL NOT NULL,
    -- The highest price of the asset across the aggregation period.
    h REAL NOT NULL,
    -- The lowest price of the asset across the aggregation period.
    l REAL NOT NULL,
    -- The closing price of the asset across the aggregation period.
    c REAL NOT NULL,
    -- The volume of shares of the asset that were traded across the period.
    v REAL NOT NULL,

    PRIMARY KEY (t, s)
);