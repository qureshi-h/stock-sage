from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, Optional
import yfinance as yf
import numpy as np
from scipy.signal import find_peaks


def fetch_stock_data(stock_symbol: str, start_date: str, end_date: str):
    data = yf.download(stock_symbol, start=start_date, end=end_date)
    if data.empty:
        raise ValueError(
            f"No data found for {stock_symbol}. Check the symbol or dates."
        )
    return data


def get_peak_indices(data, distance: int = 5) -> Tuple[np.ndarray, int]:
    highs = data["High"][:-1]  # Exclude the last day for peak calculation
    peaks, _ = find_peaks(highs, distance=distance)
    if len(peaks) == 0:
        raise ValueError("No peaks found in the data.")
    highest_peak = peaks[np.argmax(highs.iloc[peaks])]
    return peaks, highest_peak


def calculate_trendline(
    data, peaks: np.ndarray, highest_peak: int
) -> np.ndarray | None:
    highs = data["High"][:-1]
    x1, y1 = highest_peak, highs.iloc[highest_peak]
    best_slope = -np.inf

    for x2 in peaks[peaks > highest_peak]:
        y2 = highs.iloc[x2]
        slope = (y2 - y1) / (x2 - x1)
        if slope > best_slope:
            best_slope = slope

    if best_slope == -np.inf:
        # raise ValueError("Unable to calculate a valid trendline slope.")
        return None

    b = y1 - best_slope * x1
    trendline = best_slope * np.arange(len(data)) + b
    return trendline


def calculate_trendline_accuracy(
    data, peaks: np.ndarray, trendline: np.ndarray | None
) -> int | None:
    if trendline is None:
        return None
    highs = data["High"].iloc[peaks]  # Get the high values at peak positions
    trendline_at_peaks = trendline[peaks]  # Trendline values at those peaks

    within_tolerance = np.abs((highs - trendline_at_peaks) / trendline_at_peaks) <= 0.02

    accuracy = int(np.mean(within_tolerance) * 100)  # Convert to percentage
    return accuracy


def breakout_percentage(data, trendline: np.ndarray) -> float | None:
    if trendline is None:
        return None
    last_close = data["Close"].iloc[-1]
    trendline_last_day = trendline[-1]
    return (last_close - trendline_last_day) / trendline_last_day * 100


def consecutive_days_above_trendline(data, trendline: np.ndarray) -> int | None:
    if trendline is None:
        return None
    above_trend = data["Close"] > trendline[: len(data)]
    return above_trend[::-1].cumprod().sum()


def calculate_rsi(data, period: int = 14) -> float:
    delta = data["Close"].diff(1)
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]


def calculate_macd(data) -> Tuple[float, float]:
    short_ema = data["Close"].ewm(span=12, adjust=False).mean()
    long_ema = data["Close"].ewm(span=26, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd.iloc[-1], signal.iloc[-1]


def calculate_bollinger_bands(data, window: int = 20) -> Tuple[float, float, float]:
    middle_band = data["Close"].rolling(window=window).mean()
    std_dev = data["Close"].rolling(window=window).std()
    upper_band = middle_band + 2 * std_dev
    lower_band = middle_band - 2 * std_dev
    return upper_band.iloc[-1], middle_band.iloc[-1], lower_band.iloc[-1]


def calculate_emas(data) -> Dict[str, float]:
    ema_values = {
        "9EMA": data["Close"].ewm(span=9, adjust=False).mean().iloc[-1],
        "12EMA": data["Close"].ewm(span=12, adjust=False).mean().iloc[-1],
        "21EMA": data["Close"].ewm(span=21, adjust=False).mean().iloc[-1],
        "50EMA": data["Close"].ewm(span=50, adjust=False).mean().iloc[-1],
    }
    return ema_values


def volume_spike(data, window: int = 20) -> float:
    avg_volume = data["Volume"].rolling(window=window).mean()
    return data["Volume"].iloc[-1] / avg_volume.iloc[-1]


def analyse_stock(
    stock_symbol: str, end_date: Optional[str] = None, period: int = 3, data=None
) -> Dict[str, Any]:

    if end_date is None:
        end_date = datetime.today().strftime("%Y-%m-%d")

    if data is None:
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
        start_date_dt = end_date_dt - timedelta(days=period * 30)
        start_date = start_date_dt.strftime("%Y-%m-%d")
        data = fetch_stock_data(stock_symbol, start_date, end_date)

    peaks, highest_peak = get_peak_indices(data)
    trendline = calculate_trendline(data, peaks, highest_peak)
    accuracy = calculate_trendline_accuracy(data, peaks, trendline)
    ema_values = calculate_emas(data)

    results = {
        "stock_symbol": stock_symbol,
        "date": end_date,
        "close_price": float(data["Close"].iloc[-1]),
        "trendline_value": float(trendline[-1]) if trendline is not None else None,
        "breakout_percentage": breakout_percentage(data, trendline),
        "consecutive_days_above": consecutive_days_above_trendline(data, trendline),
        "trendline_accuracy": accuracy,
        "rsi": calculate_rsi(data),
        "macd_value": calculate_macd(data)[0],
        "macd_signal": calculate_macd(data)[1],
        "bollinger_upper": calculate_bollinger_bands(data)[0],
        "bollinger_middle": calculate_bollinger_bands(data)[1],
        "bollinger_lower": calculate_bollinger_bands(data)[2],
        "volume": data["Volume"].iloc[-1],
        "volume_ratio": volume_spike(data),
        "9EMA": ema_values["9EMA"],
        "12EMA": ema_values["12EMA"],
        "21EMA": ema_values["21EMA"],
        "50EMA": ema_values["50EMA"],
        "analysis_period": period * 30,
    }
    return results


if __name__ == "__main__":
    result = analyse_stock("TSLA", period=90)
    for key, value in result.items():
        print(f"{key}: {value}")
