import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime

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



def check_price_alerts(data_dict, target_prices):
     """
    Check if stock prices exceed inputted target prices above and below and print alerts.
    :param data_dict: Dictionary of ticker:DataFrame pairs
    """
     alerts = []
     for ticker in data_dict:
        if ticker in target_prices:
                    latest_price = data_dict[ticker]['Close'].iloc[-1]
                    if latest_price > target_prices[ticker]:
                       alerts.append(f"Alert: {ticker} price above target {target_prices[ticker]}!")
                    elif latest_price < target_prices[ticker]:
                        alerts.append(f"Alert: {ticker} price below target {target_prices[ticker]}!")
        return alerts

def save_to_file(data_dict, target_prices, alerts):
    """
    Save alerts to a text file and stock data to a CSV file with timestamps.
    :param data_dict: Dictionary of ticker:DataFrame pairs
    :param target_prices: Dictionary of ticker:target_price pairs
    :param alerts: List of alert messages
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("alerts.txt", "a") as f:
        for alert in alerts:
            f.write(f"{timestamp}: {alerts}\n")
    for ticker, data in data_dict.items():
            data.tail().to_csv("data_csv", mode="a", header=(ticker==list(data_dict.keys())[0]))

def main():
    tickers_input = input("Enter stock tickers (e.g., AAPL JPM, separated by space): ").upper().split()
    target_prices = {}
    for ticker in tickers_input:
        price = float(input(f"Enter target price for {ticker}: "))
        target_prices[ticker] = price
        
    try:
        data_dict = fetch_stock_data(tickers_input)
        if not data_dict:
            print("No data fetched for any ticker")
        else:
            alerts = check_price_alerts(data_dict, target_prices)# Call your alert function
            save_to_file(data_dict, target_prices, alerts) # Call your save to file feature 
            for ticker, data in data_dict.items():
                print(f"\nLatest data for {ticker}:\n", data.tail())
            plot_stock_data(data_dict)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 

