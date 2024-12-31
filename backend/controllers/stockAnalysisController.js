const { getStockAnalysisBySymbolAndDate, getTopStocks } = require('../models/stockAnalysisQueries');
const { paginate } = require('../utils/pagination');

exports.getStockAnalysis = async (req, res) => {
    try {
        const { stockSymbol } = req.params;
        const { date } = req.query;

        if (!stockSymbol || !date) {
            return res.status(400).json({ message: 'Stock symbol and date are required' });
        }

        const analysisData = await getStockAnalysisBySymbolAndDate(stockSymbol, date);

        if (analysisData.length !== 1) {
            return res
                .status(404)
                .json({ message: 'No analysis data found for the given stock symbol and date' });
        }

        res.status(200).json(analysisData[0]);
    } catch (error) {
        console.error('Error fetching stock analysis:', error.message);
        res.status(500).json({ message: 'Failed to fetch stock analysis', error: error.message });
    }
};

exports.fetchTopStocks = async (req, res) => {
    const { date } = req.query;
    const { limit, offset } = paginate(req.query.page, req.query.size);
    try {
        const data = await getTopStocks(date, limit + 1, offset);
        res.status(200).json({ rows: data.slice(0, limit), finalPage: data.length < limit + 1 });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};
