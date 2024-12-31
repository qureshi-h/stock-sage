// routes/stocks.js
const express = require('express');
const {
    fetchAllStocks,
    fetchStocksBySector,
    fetchStocksByExchange,
    fetchSingleStockByDate,
    fetchStockMultipleDates,
} = require('../controllers/stocksController');

const router = express.Router();

router.get('/all', fetchAllStocks);
router.get('/sector', fetchStocksBySector);
router.get('/exchange', fetchStocksByExchange);
router.get('/single-date', fetchSingleStockByDate);
router.get('/multiple-dates', fetchStockMultipleDates);

module.exports = router;
