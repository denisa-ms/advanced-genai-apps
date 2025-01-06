# filename: plot_stock_prices.py

import yfinance as yf
import matplotlib.pyplot as plt

# Define the stock symbols
stocks = ['META', 'TSLA']

# Fetch the stock data for the past year
data = yf.download(stocks, start='2022-01-01', end='2023-01-01')

# Calculate the daily percentage change for the 'Close' prices
data_pct_change = data['Close'].pct_change() * 100

# Plot the data
plt.figure(figsize=(14, 7))
for stock in stocks:
    plt.plot(data_pct_change[stock], label=stock)

plt.title('Daily Percentage Change in Stock Prices of META and TESLA')
plt.xlabel('Date')
plt.ylabel('Percentage Change')
plt.legend()
plt.grid(True)
plt.show()