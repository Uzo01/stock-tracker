import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import time

def fetch_stock_data(ticker: str, period="1mo", interval="1d"):
    """
    Fetch stock price data from Yahoo Finance.
    :param ticker: Stock symbol (e.g., 'AAPL' for Apple)
    :param period: Time range (e.g., '1mo', '3mo', '1y')
    :param interval: Data interval (e.g., '1d', '1h', '5m')
    :return: DataFrame with stock data
    """
    stock = yf.Ticker(ticker)
    for attempt in range(3):  # Try 3 times
        try:
            data = stock.history(period=period, interval=interval)
            if not data.empty:
                return data
            else:
                print(f"Empty data returned for {ticker}, retrying...")
        except yfinance.exceptions.YFException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < 2:  # Wait before retrying
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
    raise Exception(f"Failed to fetch data for {ticker} after 3 attempts")

def plot_stock_data(data, ticker):
    """
    Plot closing prices for the given stock data.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Close'], label=f"{ticker} Closing Price", color="blue")
    plt.title(f"{ticker} Stock Price")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    ticker = input("Enter stock ticker (e.g., AAPL for Apple): ").upper()
    try:
        data = fetch_stock_data(ticker)
        print("\nLatest data:\n", data.tail())  # Show last few rows
        plot_stock_data(data, ticker)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()