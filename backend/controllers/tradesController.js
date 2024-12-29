const { createTrade, getAllTrades, getTraderHoldingsByType } = require('../models/tradeQueries');

// Controller for creating a new trade
exports.createTrade = async (req, res) => {
    try {
        const {
            stock_id,
            trader_name,
            trade_type,
            price,
            trade_date,
            units,
            rationale,
            option_type,
            strike_price,
            expiration_date,
        } = req.body;

        const trade = await createTrade({
            stock_id,
            trader_name,
            trade_type,
            price,
            trade_date,
            units,
            rationale,
            option_type,
            strike_price,
            expiration_date,
        });

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

        // Set Cache-Control header to refresh every 5 minutes
        res.setHeader('Cache-Control', 'public, max-age=300, stale-while-revalidate=60');

        return res.status(200).json(trades);
    } catch (error) {
        console.error('Error fetching trades:', error.message);
        return res.status(500).json({ message: 'Failed to fetch trades', error: error.message });
    }
};

// Controller for fetching trader holdings by type (stock or option)
exports.getTraderHoldingsByType = async (req, res) => {
    try {
        const { traderName } = req.params;
        const { trade_type } = req.query;

        if (!traderName) {
            return res.status(400).json({ message: 'Trader name is required' });
        }

        if (!['stock', 'options'].includes(trade_type)) {
            return res.status(400).json({ message: "Type must be either 'stock' or 'options'" });
        }

        const holdings = await getTraderHoldingsByType(traderName, trade_type);

        if (holdings.length === 0) {
            return res
                .status(404)
                .json({ message: `No ${trade_type}s found for the given trader` });
        }

        res.status(200).json({ trader: traderName, trade_type, holdings });
    } catch (error) {
        console.error('Error fetching trader holdings:', error.message);
        res.status(500).json({ message: 'Failed to fetch trader holdings', error: error.message });
    }
};
