import psycopg2
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

from stock_analysis import analyse_stock, fetch_stock_data


class StockAnalysisDatabase:
    """Class to manage stock operations and store analysis results."""

    def __init__(
        self,
    ):
        """Initialize the database connection."""
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )

    def fetch_all_stocks(self) -> List[Dict[str, Any]]:
        """Fetch all stocks from the database."""
        query = "SELECT stock_id, stock_symbol FROM stocks;"
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            stocks = cursor.fetchall()
        return [{"stock_id": row[0], "stock_symbol": row[1]} for row in stocks[:]]

    def insert_analysis(self, stock_id: int, analysis: Dict[str, Any]):
        """Insert stock analysis result into the database with proper type conversion."""
        query = """
            INSERT INTO stock_analysis (
                stock_id, analysis_date, analysis_period, close_price, breakout_percentage, 
                consecutive_days_above_trendline, trendline_accuracy, rsi_value, 
                macd_value, macd_signal, upper_bollinger_band, 
                middle_bollinger_band, lower_bollinger_band, volume, volume_ratio,
                nine_ema, twelve_ema, twenty_one_ema, fifty_ema
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (stock_id, analysis_date, analysis_period) DO NOTHING;
        """
        with self.conn.cursor() as cursor:
            data = (
                stock_id,
                analysis["date"],
                analysis["analysis_period"],
                float(round(analysis["close_price"], 3)),
                (
                    float(round(analysis["breakout_percentage"], 3))
                    if analysis["breakout_percentage"] is not None
                    else None
                ),
                (
                    int(analysis["consecutive_days_above"])
                    if analysis["consecutive_days_above"] is not None
                    else None
                ),
                (
                    float(round(analysis["trendline_accuracy"], 3))
                    if analysis["trendline_accuracy"] is not None
                    else None
                ),
                float(round(analysis["rsi"], 3)),
                float(round(analysis["macd_value"], 3)),
                float(round(analysis["macd_signal"], 3)),
                float(round(analysis["bollinger_upper"], 3)),
                float(round(analysis["bollinger_middle"], 3)),
                float(round(analysis["bollinger_lower"], 3)),
                int(analysis["volume"]),
                float(round(analysis["volume_ratio"], 3)),
                float(round(analysis["9EMA"], 3)),
                float(round(analysis["12EMA"], 3)),
                float(round(analysis["21EMA"], 3)),
                float(round(analysis["50EMA"], 3)),
            )

            cursor.execute(query, data)
            self.conn.commit()

    def analyse_and_store_stocks(
        self, analysis_date: Optional[str] = None, period: int = 3
    ):
        """Run analysis on all stocks and store results in the database."""
        if analysis_date is None:
            analysis_date = datetime.today().strftime("%Y-%m-%d")
        analysis_date_dt = datetime.strptime(analysis_date, "%Y-%m-%d")

        # Check if the analysis date is a weekend (Saturday or Sunday)
        if analysis_date_dt.weekday() >= 5:  # 5: Saturday, 6: Sunday
            print(
                f"Your chosen date ({analysis_date}) falls on a weekend. No analysis will be performed."
            )
            return

        stocks = self.fetch_all_stocks()
        successful = 0
        for stock in stocks:
            try:
                print(f"Analyzing {stock['stock_symbol']}...")
                result = analyse_stock(stock["stock_symbol"], analysis_date, period)
                self.insert_analysis(stock["stock_id"], result)
                print(
                    f"Inserted analysis for {stock['stock_symbol']} on {analysis_date}."
                )
                successful += 1
            except Exception as e:
                print(f"Error analyzing {stock['stock_symbol']}: {e}")
        total = len(stocks)
        print(
            f"{successful} out of {total} successfully analysed ({successful / total * 100:.2f}%)"
        )

    def backtest_stocks(
        self,
        stock_symbols: List[str],
        start_date: str,
        days: int = 365,
        analysis_window: int = 90,
    ):
        """
        Backtest the analysis by simulating daily analysis for a 180-day period within a 1-year historical range.

        Parameters:
        - stock_symbols: List of stock symbols to backtest.
        - start_date: Start date for the backtesting period in "YYYY-MM-DD" format.
        - days: Total number of days for backtesting, default is 365 (1 year).
        - analysis_window: Number of days for each analysis window, default is 90 days.
        """
        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_dt = start_date_dt + timedelta(days=days)

        for symbol in stock_symbols:
            print(
                f"Backtesting for {symbol} from {start_date} to {end_date_dt.strftime('%Y-%m-%d')}"
            )
            try:
                data = fetch_stock_data(
                    symbol, start_date, end_date_dt.strftime("%Y-%m-%d")
                )
                if data.empty:
                    print(f"No data for {symbol}, skipping.")
                    continue

                stock_id = self.get_stock_id(symbol)

                # Run analysis every day within the backtesting range, focusing on the last 180 days each time
                for current_date in (
                    start_date_dt + timedelta(days=i)
                    for i in range(days - analysis_window + 1)
                ):
                    analysis_end_date = current_date + timedelta(days=analysis_window)

                    # Skip weekends directly using weekday check (5 = Saturday, 6 = Sunday)
                    if analysis_end_date.weekday() >= 5:
                        continue

                    # Check if analysis_end_date is in data to avoid KeyError
                    if analysis_end_date not in data.index:
                        print(
                            f"Skipping {analysis_end_date} for {symbol} as it's missing in data."
                        )
                        continue

                    window_data = data.loc[
                        current_date.strftime("%Y-%m-%d") : analysis_end_date.strftime(
                            "%Y-%m-%d"
                        )
                    ]

                    try:
                        result = analyse_stock(
                            symbol,
                            analysis_end_date.strftime("%Y-%m-%d"),
                            data=window_data,
                        )
                        # Assuming the stock ID is retrieved or matched based on the stock symbol
                        if stock_id:
                            self.insert_analysis(stock_id, result)
                            print(
                                f"Inserted backtest analysis for {symbol} on {analysis_end_date.strftime('%Y-%m-%d')}"
                            )
                            self.insert_max_price_analysis(
                                stock_id,
                                analysis_end_date.strftime("%Y-%m-%d"),
                                data,
                            )
                            print(
                                f"Inserted max price analysis for {symbol} on {analysis_end_date.strftime('%Y-%m-%d')}."
                            )
                        else:
                            print(f"Stock ID for {symbol} not found, skipping.")
                    except Exception as e:
                        print(
                            f"Error during backtest analysis for {symbol} on {analysis_end_date}: {e}"
                        )
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")

    def insert_max_price_analysis(self, stock_id: int, analysis_date: str, data):
        """
        Calculate and insert max prices for 1, 2, 7, 14, 21, and 30 days following the analysis date.

        Parameters:
        - stock_id: ID of the stock being analyzed.
        - analysis_date: Date of the analysis.
        - data: DataFrame with historical stock data that includes the dates following the analysis date.
        """
        analysis_date_dt = datetime.strptime(analysis_date, "%Y-%m-%d")

        # Find the index for the analysis date
        analysis_index = data.index.get_loc(analysis_date_dt)

        # Define maximum price fields for different time windows
        max_prices = {
            "max_price_1_day": (
                data["High"].iloc[analysis_index : analysis_index + 1].max()
                if analysis_index < len(data)
                else None
            ),
            "max_price_2_days": (
                data["High"].iloc[analysis_index : analysis_index + 2].max()
                if analysis_index + 1 < len(data)
                else None
            ),
            "max_price_5_days": (
                data["High"].iloc[analysis_index : analysis_index + 5].max()
                if analysis_index + 4 < len(data)
                else None
            ),
            "max_price_10_days": (
                data["High"].iloc[analysis_index : analysis_index + 10].max()
                if analysis_index + 9 < len(data)
                else None
            ),
            "max_price_15_days": (
                data["High"].iloc[analysis_index : analysis_index + 15].max()
                if analysis_index + 14 < len(data)
                else None
            ),
            "max_price_20_days": (
                data["High"].iloc[analysis_index : analysis_index + 20].max()
                if analysis_index + 19 < len(data)
                else None
            ),
        }

        # Insert max prices into the stock_analysis_max_price table
        query = """
            INSERT INTO stock_analysis_max_price (
                stock_id, analysis_date, max_price_1_day, max_price_2_days, max_price_5_days, 
                max_price_10_days, max_price_15_days, max_price_20_days
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (stock_id, analysis_date) DO UPDATE SET
                max_price_1_day = EXCLUDED.max_price_1_day,
                max_price_2_days = EXCLUDED.max_price_2_days,
                max_price_5_days = EXCLUDED.max_price_5_days,
                max_price_10_days = EXCLUDED.max_price_10_days,
                max_price_15_days = EXCLUDED.max_price_15_days,
                max_price_20_days = EXCLUDED.max_price_20_days;
        """
        with self.conn.cursor() as cursor:
            cursor.execute(
                query,
                (
                    stock_id,
                    analysis_date,
                    (
                        float(max_prices["max_price_1_day"])
                        if max_prices["max_price_1_day"]
                        else None
                    ),
                    (
                        float(max_prices["max_price_2_days"])
                        if max_prices["max_price_2_days"]
                        else None
                    ),
                    (
                        float(max_prices["max_price_5_days"])
                        if max_prices["max_price_5_days"]
                        else None
                    ),
                    (
                        float(max_prices["max_price_10_days"])
                        if max_prices["max_price_10_days"]
                        else None
                    ),
                    (
                        float(max_prices["max_price_15_days"])
                        if max_prices["max_price_15_days"]
                        else None
                    ),
                    (
                        float(max_prices["max_price_20_days"])
                        if max_prices["max_price_20_days"]
                        else None
                    ),
                ),
            )
            self.conn.commit()

    def get_stock_id(self, stock_symbol: str) -> Optional[int]:
        """Fetch the stock ID from the database based on the stock symbol."""
        query = "SELECT stock_id FROM stocks WHERE stock_symbol = %s;"
        with self.conn.cursor() as cursor:
            cursor.execute(query, (stock_symbol,))
            result = cursor.fetchone()
        return result[0] if result else None

    def fetch_breakout_data_with_max_prices(
        self, stock_symbol: str, start_date: str = "2020-01-01", end_date: str = None
    ):
        """
        Fetch all analysis records for the specified stock where breakout_percentage > 0
        within the given date range, including max price data.

        Parameters:
        - stock_symbol: The stock symbol to filter records.
        - start_date: Start date for filtering, default is "2020-01-01".
        - end_date: End date for filtering, default is today's date.

        Returns:
        - DataFrame containing the analysis data with max prices where breakout_percentage > 0.
        """
        if end_date is None:
            end_date = datetime.today().strftime("%Y-%m-%d")

        # Fetch stock ID based on the stock symbol
        stock_id = self.get_stock_id(stock_symbol)
        if not stock_id:
            print(f"Stock ID for symbol '{stock_symbol}' not found.")
            return None

        query = """
            SELECT sa.*, mp.max_price_1_day, mp.max_price_2_days, mp.max_price_5_days,
                mp.max_price_10_days, mp.max_price_15_days, mp.max_price_20_days
            FROM stock_analysis sa
            LEFT JOIN stock_analysis_max_price mp
            ON sa.stock_id = mp.stock_id
            AND sa.analysis_date = mp.analysis_date
            WHERE sa.stock_id = %s
            AND sa.analysis_date BETWEEN %s AND %s
            AND sa.breakout_percentage > 0
            AND sa.consecutive_days_above_trendline = 1;
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query, (stock_id, start_date, end_date))
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

        # Convert data to a DataFrame for easy analysis
        df = pd.DataFrame(data, columns=columns)
        if df.empty:
            print("No breakout data found for the specified criteria.")
        return df

    def plot_breakout_and_max_prices(self, df, stock_symbol):
        # Ensure there are data to plot
        if df.empty:
            print("No data to plot.")
            return

        # Convert analysis_date to datetime for easier plotting
        df["analysis_date"] = pd.to_datetime(df["analysis_date"])

        fig, ax1 = plt.subplots(figsize=(14, 8))

        # Plot breakout percentage as bars on secondary y-axis
        ax2 = ax1.twinx()
        ax2.bar(
            df["analysis_date"],
            df["breakout_percentage"],
            label="Breakout Percentage",
            color="skyblue",
            alpha=0.6,
        )
        ax2.set_ylabel("Breakout Percentage", color="skyblue")
        ax2.tick_params(axis="y", labelcolor="skyblue")

        # Plot close price and max prices on primary y-axis
        ax1.plot(
            df["analysis_date"],
            df["close_price"],
            label="Close Price",
            color="purple",
            linestyle="--",
            marker="o",
        )

        # Overlay with line plots of max prices
        ax1.plot(
            df["analysis_date"],
            df["max_price_1_day"],
            label="Max Price 1 Day",
            marker="o",
        )
        ax1.plot(
            df["analysis_date"],
            df["max_price_2_days"],
            label="Max Price 2 Days",
            marker="o",
        )
        ax1.plot(
            df["analysis_date"],
            df["max_price_5_days"],
            label="Max Price 5 Days",
            marker="o",
        )
        ax1.plot(
            df["analysis_date"],
            df["max_price_10_days"],
            label="Max Price 10 Days",
            marker="o",
        )
        ax1.plot(
            df["analysis_date"],
            df["max_price_15_days"],
            label="Max Price 15 Days",
            marker="o",
        )
        ax1.plot(
            df["analysis_date"],
            df["max_price_20_days"],
            label="Max Price 20 Days",
            marker="o",
        )

        # Add labels, titles, and legend
        ax1.set_title(f"{stock_symbol} Breakout Percentage and Max Prices Over Time")
        ax1.set_xlabel("Analysis Date")
        ax1.set_ylabel("Price", color="purple")
        ax1.tick_params(axis="y", labelcolor="purple")
        ax1.set_ylim(bottom=80)

        # Combine legends from both axes
        lines, labels = ax1.get_legend_handles_labels()
        bars, bar_labels = ax2.get_legend_handles_labels()
        ax1.legend(lines + bars, labels + bar_labels, loc="upper left")

        # Format x-axis
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def close_connection(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    db = StockAnalysisDatabase()
    db.analyse_and_store_stocks(period=3)
    db.close_connection()
