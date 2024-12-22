const { createTrade, getAllTrades } = require('../models/tradeQueries');

// Controller for creating a new trade
exports.createTrade = async (req, res) => {
    try {
        const trade = await createTrade(req.body);
        console.log(req.body);

        res.status(201).json({ message: 'Trade created successfully', trade });
    } catch (error) {
        console.error('Error creating trade:', error.message);
        res.status(500).json({ message: 'Failed to create trade', error: error.message });
    }
};

// Controller for fetching all trades
exports.getTrades = async (req, res) => {
    try {
        const trades = await getAllTrades();
        res.status(200).json(trades);
    } catch (error) {
        console.error('Error fetching trades:', error.message);
        res.status(500).json({ message: 'Failed to fetch trades', error: error.message });
    }
};
