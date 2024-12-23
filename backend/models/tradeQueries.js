const pool = require('../config/db');

// Create a new trade
const createTrade = async ({
    stock_id,
    trader_name,
    trade_type,
    price,
    trade_date,
    units,
    rationale,
    option_type,
    strike_price,
    expiration_date,
}) => {
    const query = `
        INSERT INTO trades 
        (stock_id, trader_name, trade_type, price, trade_date, units, rationale, 
        option_type, strike_price, expiration_date)
        VALUES 
        ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        RETURNING *;
    `;
    const values = [
        stock_id,
        trader_name,
        trade_type,
        price,
        trade_date,
        units,
        rationale,
        option_type,
        strike_price,
        expiration_date,
    ];

    const { rows } = await pool.query(query, values);
    return rows[0]; // Return the created trade
};

// Fetch all trades
const getAllTrades = async () => {
    const query = `
        SELECT 
            t.trade_id, 
            t.stock_id, 
            t.trader_name, 
            t.trade_type, 
            t.price, 
            t.trade_date, 
            t.units, 
            t.rationale,
            t.option_type, 
            t.strike_price, 
            t.expiration_date, 
            s.stock_symbol,
            s.stock_name,
            s.sector,
            s.exchange
        FROM trades t
        INNER JOIN stocks s ON t.stock_id = s.stock_id;
    `;
    const { rows } = await pool.query(query);
    return rows; // Return the list of trades
};

// Get current holdings (stocks or options) for a trader
const getTraderHoldingsByType = async (traderName, type) => {
    const query =
        type === 'stock'
            ? `
            SELECT 
                s.stock_id,
                s.stock_symbol,
                s.stock_name,
                s.sector,
                s.exchange,
                COALESCE(SUM(CASE WHEN t.trade_type = 'buy' THEN t.units ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN t.trade_type = 'sell' THEN t.units ELSE 0 END), 0) AS net_units
            FROM trades t
            JOIN stocks s ON t.stock_id = s.stock_id
            WHERE t.trader_name = $1 AND t.option_type IS NULL
            GROUP BY s.stock_id, s.stock_symbol, s.stock_name, s.sector, s.exchange
            HAVING COALESCE(SUM(CASE WHEN t.trade_type = 'buy' THEN t.units ELSE 0 END), 0) -
                   COALESCE(SUM(CASE WHEN t.trade_type = 'sell' THEN t.units ELSE 0 END), 0) > 0;
        `
            : `
            SELECT 
                s.stock_id,
                s.stock_symbol,
                s.stock_name,
                s.sector,
                s.exchange,
                COALESCE(SUM(CASE WHEN t.trade_type = 'buy' THEN t.units ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN t.trade_type = 'sell' THEN t.units ELSE 0 END), 0) AS net_units
            FROM trades t
            JOIN stocks s ON t.stock_id = s.stock_id
            WHERE t.trader_name = $1 AND t.option_type IS NOT NULL
            GROUP BY s.stock_id, s.stock_symbol, s.stock_name, s.sector, s.exchange
            HAVING COALESCE(SUM(CASE WHEN t.trade_type = 'buy' THEN t.units ELSE 0 END), 0) -
                   COALESCE(SUM(CASE WHEN t.trade_type = 'sell' THEN t.units ELSE 0 END), 0) > 0;
        `;

    const { rows } = await pool.query(query, [traderName]);
    return rows;
};

module.exports = {
    createTrade,
    getAllTrades,
    getTraderHoldingsByType,
};
