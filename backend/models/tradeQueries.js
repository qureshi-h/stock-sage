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
    option_contracts,
}) => {
    const query = `
        INSERT INTO trades 
        (stock_id, trader_name, trade_type, price, trade_date, units, rationale, 
        option_type, strike_price, expiration_date, option_contracts)
        VALUES 
        ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
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
        option_contracts,
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
            t.option_contracts,
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

module.exports = {
    createTrade,
    getAllTrades,
};
