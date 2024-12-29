const pool = require('../config/db');

// Get stock analysis for a given stock_symbol and date
const getStockAnalysisBySymbolAndDate = async (stockSymbol, analysisDate) => {
    const query = `
        SELECT 
            sa.analysis_id,
            sa.stock_id,
            sa.analysis_date,
            sa.analysis_period,
            sa.close_price,
            sa.breakout_percentage,
            sa.consecutive_days_above_trendline,
            sa.trendline_accuracy,
            sa.rsi_value,
            sa.macd_value,
            sa.macd_signal,
            sa.upper_bollinger_band,
            sa.middle_bollinger_band,
            sa.lower_bollinger_band,
            sa.volume_ratio,
            sa.created_at,
            sa.volume,
            sa.nine_ema,
            sa.twelve_ema,
            sa.twenty_one_ema,
            sa.fifty_ema
        FROM public.stock_analysis sa
        JOIN public.stocks s ON sa.stock_id = s.stock_id
        WHERE s.stock_symbol = $1 AND sa.analysis_date = $2;
    `;

    const values = [stockSymbol, analysisDate];

    const { rows } = await pool.query(query, values);
    return rows;
};

module.exports = {
    getStockAnalysisBySymbolAndDate,
};
