CREATE TABLE trades (
    trade_id SERIAL PRIMARY KEY,            -- Unique identifier for each trade
    stock_id INTEGER NOT NULL,              -- References the stocks table for stock trades
    trader_name VARCHAR(50) NOT NULL,       -- Trader's name
    trade_type VARCHAR(10) NOT NULL,        -- Buy or Sell
    price NUMERIC(10, 2) NOT NULL,          -- Price of the trade (can be the stock price or the option premium)
    trade_date DATE NOT NULL,               -- Date of the trade
    units INTEGER NOT NULL,                 -- Number of units for stocks or number of options contracts
    rationale TEXT NOT NULL,                -- Reason for the trade
    option_type VARCHAR(10),                -- 'call' or 'put' for options trades, NULL for stock trades
    strike_price NUMERIC(10, 2),            -- Strike price of the option (NULL for stock trades)
    expiration_date DATE,                   -- Expiration date of the option (NULL for stock trades)
    option_contracts INTEGER,               -- Number of option contracts (NULL for stock trades)
    created_at TIMESTAMP DEFAULT NOW(),     -- Timestamp for when the record is created
    updated_at TIMESTAMP DEFAULT NOW(),     -- Timestamp for when the record is updated
    CONSTRAINT fk_stock FOREIGN KEY (stock_id)
        REFERENCES stocks (stock_id)
        ON DELETE CASCADE                   -- Delete trades if the stock is removed
        ON UPDATE CASCADE                   -- Update stock_id in trades if it changes in stocks
);

-- Optional: Index for faster querying by stock_id
CREATE INDEX idx_trades_stock_id ON trades (stock_id);
