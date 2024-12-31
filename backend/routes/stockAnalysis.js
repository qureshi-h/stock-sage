const express = require('express');
const router = express.Router();

const { fetchTopStocks, getStockAnalysis } = require('../controllers/stockAnalysisController');

router.get('/top', fetchTopStocks);
router.get('/:stockSymbol', getStockAnalysis);

module.exports = router;
