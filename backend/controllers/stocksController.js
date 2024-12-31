// controllers/stocksController.js
const {
    getStock,
    getAllStocks,
    getStocksBySector,
    getStocksByExchange,
    getSingleStockByDate,
    getStockMultipleDates,
} = require('../models/stockQueries');

exports.fetchStock = async (req, res) => {
    try {
        const { stock } = req.params;
        const data = await getStock(stock);

        if (data === null) {
            return res.status(404).json({ message: 'Stock Not Found!' });
        }

        return res.status(200).json(data);
    } catch (error) {
        return res.status(500).json({ message: error.message });
    }
};

exports.fetchAllStocks = async (_, res) => {
    try {
        const data = await getAllStocks();
        return res.status(200).json(data);
    } catch (error) {
        return res.status(500).json({ message: error.message });
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
