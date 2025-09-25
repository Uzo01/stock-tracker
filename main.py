import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

class StockTrackerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stock Tracker")
        self.root.geometry("500x400")

        tk.Label(self.root, text="Investment Backtest", font=("Arial", 16)).pack(pady=10)
        
        self.tree = ttk.Treeview(self.root, columns=("Month", "Amount"), show="headings")
        self.tree.heading("Month", text="Month")
        self.tree.heading("Amount", text="Amount (£)")
        self.tree.pack(pady=10, fill="both", expand=True)

        for month in range(1, 13):
            self.tree.insert("", "end", values=(month, 1000))
        self.tree.bind("<Double-1>", self.edit_cell)
        
        tk.Button(self.root, text="Run Backtest", command=self.run_backtest).pack(pady=5)
        tk.Button(self.root, text="View Results", command=self.view_results).pack(pady=5)
        tk.Button(self.root, text="Save to Excel", command=self.save_excel).pack(pady=5)
        tk.Button(self.root, text="Exit", command=self.root.quit).pack(pady=5)

        self.root.mainloop()
    
    def edit_cell(self, event):
        item = self.tree.identify_row(event.y)
        if item and self.tree.identify_column(event.x) == "#2":
            entry = tk.Entry(self.root)
            entry.place(x=event.x, y=event.y, anchor="w")
            entry.insert(0, self.tree.item(item, "values")[1])
            def save_edit(event):
                new_value = entry.get()
                if new_value.replace(".", "").isdigit():
                    self.tree.set(item, column="#2", value=new_value)
                entry.destroy()
            entry.bind("<Return>", save_edit)
            entry.bind("<FocusOut>", save_edit)
    
    def run_backtest(self):
        variable_amounts = [float(self.tree.item(item)['values'][1]) for item in self.tree.get_children()]
        if len(variable_amounts) != 12:
            messagebox.showerror("Error", "Please enter amounts for all 12 months.")
            return
        try:
            self.backtest_df = backtest_investment(variable_amounts)
            messagebox.showinfo("Backtest", "Backtest completed! View results.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def view_results(self):
        if hasattr(self, 'backtest_df'):
            try:
                plt.figure(figsize=(10, 6))
                plt.plot(self.backtest_df['Date'], self.backtest_df['Current Value'], label="Portfolio Value")
                plt.title("Investment Growth")
                plt.xlabel("Date")
                plt.ylabel("Value (£)")
                plt.legend()
                plt.grid(True)
                plt.show()
            except Exception as e:
                messagebox.showerror("Plot Error", f"Error plotting: {e}")
        else:
            messagebox.showwarning("No Results", "Run backtest first!")
    
    def save_excel(self):
        if hasattr(self, 'backtest_df'):
            try:
                self.backtest_df.to_excel("backtest_results.xlsx", index=False)
                messagebox.showinfo("Saved", "Results saved to backtest_results.xlsx!")
            except Exception as e:
                messagebox.showerror("Save Error", f"Error saving: {e}")
        else:
            messagebox.showwarning("No Results", "Run backtest first!")

def backtest_investment(variable_amounts):
    """
    Backtest variable monthly investments in S&P 500 over the past year.
    :param variable_amounts: List of monthly investment amounts (£)
    :return: DataFrame with investment results
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    sp500 = yf.download('^GSPC', start=start_date, end=end_date, progress=False)
    
    months = len(variable_amounts)
    investment_dates = pd.date_range(start=start_date, periods=months, freq='MS')
    portfolio = []
    total_invested = 0
    total_shares = 0
    
    if not all(isinstance(x, (int, float)) and x > 0 for x in variable_amounts):
        raise ValueError("All investment amounts must be positive numbers.")
    if months > len(sp500):
        months = len(sp500)
        investment_dates = investment_dates[:months]
    
    for i, date in enumerate(investment_dates[:months]):
        price = sp500['Close'].asof(date)
        if price <= 0:
            print(f"Warning: Invalid price at {date}, skipping month.")
            continue
        amount = variable_amounts[i]
        shares_bought = amount / price
        total_shares += shares_bought
        total_invested += amount
        current_value = total_shares * sp500['Close'].iloc[-1]
        growth = current_value - total_invested
        portfolio.append({
            'Date': date,
            'Amount': amount,
            'Price': price,
            'Shares Bought': shares_bought,
            'Total Invested': total_invested,
            'Current Value': current_value,
            'Growth': growth
        })
    
    df = pd.DataFrame(portfolio)
    return df

def fetch_stock_data(tickers: list, period="1mo", interval="1d"):
    """
    Fetch stock price data from Yahoo Finance.
    :param tickers: List of stock symbols (e.g., ['AAPL', 'JPM'])
    :param period: Time range (e.g., '1mo', '3mo', '1y')
    :param interval: Data interval (e.g., '1d', '1h', '5m')
    :return: Dictionary of ticker:DataFrame pairs
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
    :param target_prices: Dictionary of ticker:target_price pairs
    :return: List of alert messages
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
            f.write(f"{timestamp}: {alert}\n")
    for ticker, data in data_dict.items():
        data.tail().to_csv("data.csv", mode="a", header=(ticker == list(data_dict.keys())[0]))

if __name__ == "__main__":
    app = StockTrackerApp()