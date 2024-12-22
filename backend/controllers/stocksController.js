// controllers/stocksController.js
const {
    getAllStocks,
    getTopStocks,
    getStocksBySector,
    getStocksByExchange,
    getSingleStockByDate,
    getStockMultipleDates,
} = require('../models/stockQueries');
const { paginate } = require('../utils/pagination');

exports.fetchAllStocks = async (_, res) => {
    try {
        const data = await getAllStocks();
        res.status(200).json(data);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

exports.fetchTopStocks = async (req, res) => {
    const { date } = req.query;
    const { limit, offset } = paginate(req.query.page, req.query.size);
    try {
        const data = await getTopStocks(date, limit, offset);
        res.status(200).json(data);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

exports.fetchStocksBySector = async (req, res) => {
    const { date, sector } = req.query;
    try {
        const data = await getStocksBySector(date, sector);
        res.status(200).json(data);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

exports.fetchStocksByExchange = async (req, res) => {
    const { date, exchange } = req.query;
    try {
        const data = await getStocksByExchange(date, exchange);
        res.status(200).json(data);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

exports.fetchSingleStockByDate = async (req, res) => {
    const { symbol, date } = req.query;
    try {
        const data = await getSingleStockByDate(symbol, date);
        res.status(200).json(data);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

exports.fetchStockMultipleDates = async (req, res) => {
    const { symbol, startDate, endDate } = req.query;
    try {
        const data = await getStockMultipleDates(symbol, startDate, endDate);
        res.status(200).json(data);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};
