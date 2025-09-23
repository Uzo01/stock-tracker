import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import time

def fetch_stock_data(tickers: list, period="1mo", interval="1d"):
    """
    Fetch stock price data from Yahoo Finance.
    :param ticker: Stock symbol (e.g., 'AAPL' for Apple)
    :param period: Time range (e.g., '1mo', '3mo', '1y')
    :param interval: Data interval (e.g., '1d', '1h', '5m')
    :return: DataFrame with stock data
    """
    data_dict = {}
    for ticker in tickers:
        for attempt in range(3):
            try:
                stock = yf.Ticker(ticker)
                data = stock.history(period=period, interval=interval)
                if not data.empty:
                    data_dict[ticker] = data
                    break
                else:
                    print(f"Empty data for {ticker}, retrying...")
            except yfinance.exceptions.YFException as e:
                print(f"Attempt {attempt + 1} failed for {ticker}: {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
        else:
            print(f"Failed to fetch data for {ticker} after 3 attempts")
    return data_dict

def plot_stock_data(data_dict):
    """
    Plot closing prices for multiple stocks from a dictionary of data.
    :param data_dict: Dictionary of ticker:DataFrame pairs
    """
    plt.figure(figsize=(12, 8))
    for ticker, data in data_dict.items():
        if not data.empty:
            plt.plot(data.index, data['Close'], label=f"{ticker} Closing Price")
    plt.title("Multiple Stock Prices")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.show()

def check_price_alerts(data_dict):
    """
    Check if stock prices exceed hardcoded target prices and print alerts.
    :param data_dict: Dictionary of ticker:DataFrame pairs
    """
    default_targets = {"AAPL": 150, "JPM": 200}
    for ticker in data_dict:
        if ticker in default_targets:
            latest_price = data_dict[ticker]['Close'].iloc[-1]
            if latest_price > default_targets[ticker]:
                print(f"Alert: {ticker} price above target {default_targets[ticker]}!")
def main():
    tickers_input = input("Enter stock tickers (e.g., AAPL JPM, separated by space): ").upper().split()
    try:
        data_dict = fetch_stock_data(tickers_input)
        if not data_dict:
            print("No data fetched for any ticker")
        else:
            check_price_alerts(data_dict)  # Call your alert function
            for ticker, data in data_dict.items():
                print(f"\nLatest data for {ticker}:\n", data.tail())
            plot_stock_data(data_dict)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 

