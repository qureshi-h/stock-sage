const express = require('express');
const router = express.Router();
const tradeController = require('../controllers/tradesController');

// Endpoint to create a trade
router.post('/', tradeController.createTrade);

// Endpoint to get all trades
router.get('/', tradeController.getTrades);

// Route to get trader's current stock holdings
router.get('/holdings/:traderName', tradeController.getTraderHoldingsByType);

module.exports = router;
