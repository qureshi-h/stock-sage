// models/stockQueries.js

const pool = require('../config/db');

const getStock = async (stock) => {
    const query = `
      SELECT stock_id, stock_name, stock_symbol, sector, exchange
      FROM stocks
      WHERE stock_symbol = $1;
    `;
    const { rows } = await pool.query(query, [stock]);
    return rows.length === 1 ? rows[0] : null;
};

const getAllStocks = async () => {
    const query = `
    SELECT stock_id, stock_name, stock_symbol, sector, exchange
    FROM stocks;
  `;
    const { rows } = await pool.query(query);
    return rows;
};

const getTopStocks = async (date, limit, offset) => {
    const query = `
    SELECT s.stock_symbol, s.stock_name, sa.*
    FROM stock_analysis sa
    JOIN stocks s ON sa.stock_id = s.stock_id
    WHERE sa.analysis_date = $1
    ORDER BY sa.breakout_percentage DESC
    LIMIT $2 OFFSET $3;
  `;
    const { rows } = await pool.query(query, [date, limit, offset]);
    return rows;
};

const getStocksBySector = async (date, sector) => {
    const query = `
    SELECT s.stock_symbol, s.stock_name, sa.*
    FROM stock_analysis sa
    JOIN stocks s ON sa.stock_id = s.stock_id
    WHERE sa.analysis_date = $1 AND s.sector = $2;
  `;
    const { rows } = await pool.query(query, [date, sector]);
    return rows;
};

const getStocksByExchange = async (date, exchange) => {
    const query = `
    SELECT s.stock_symbol, s.stock_name, sa.*
    FROM stock_analysis sa
    JOIN stocks s ON sa.stock_id = s.stock_id
    WHERE sa.analysis_date = $1 AND s.exchange = $2;
  `;
    const { rows } = await pool.query(query, [date, exchange]);
    return rows;
};

const getSingleStockByDate = async (symbol, date) => {
    const query = `
    SELECT s.stock_symbol, s.stock_name, sa.*
    FROM stock_analysis sa
    JOIN stocks s ON sa.stock_id = s.stock_id
    WHERE s.stock_symbol = $1 AND sa.analysis_date = $2;
  `;
    const { rows } = await pool.query(query, [symbol, date]);
    return rows[0];
};

const getStockMultipleDates = async (symbol, startDate, endDate) => {
    const query = `
    SELECT s.stock_symbol, s.stock_name, sa.*
    FROM stock_analysis sa
    JOIN stocks s ON sa.stock_id = s.stock_id
    WHERE s.stock_symbol = $1 AND sa.analysis_date BETWEEN $2 AND $3;
  `;
    const { rows } = await pool.query(query, [symbol, startDate, endDate]);
    return rows;
};

module.exports = {
    getStock,
    getAllStocks,
    getTopStocks,
    getStocksBySector,
    getStocksByExchange,
    getSingleStockByDate,
    getStockMultipleDates,
};
