const express = require('express');
const { getStockAnalysis } = require('../controllers/stockAnalysisController');
const router = express.Router();

router.get('/:stockSymbol/', getStockAnalysis);

module.exports = router;
