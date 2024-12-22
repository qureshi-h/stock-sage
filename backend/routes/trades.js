const express = require('express');
const router = express.Router();
const tradeController = require('../controllers/tradesController');

// Endpoint to create a trade
router.post('/', tradeController.createTrade);

// Endpoint to get all trades
router.get('/', tradeController.getTrades);

module.exports = router;
