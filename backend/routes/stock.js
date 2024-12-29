// routes/stocks.js
const express = require('express');
const { fetchStock } = require('../controllers/stocksController');

const router = express.Router();

router.get('/:stock', fetchStock);

module.exports = router;
