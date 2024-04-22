import yfinance as yf
import json

# Function to extract close prices for specific dates from Yahoo Finance
def extract_close_prices(ticker):
    # Fetch OHLC data from Yahoo Finance
    try:
        data = yf.download(ticker, start='2010-03-01', end='2023-12-31', interval='3mo')['Close']
        # Check if any data is missing
        if data.empty or data.isnull().values.any():
            return None
        else:
            return data
    except ValueError:
        return None

# Function to calculate yearly average close price
def calculate_yearly_avg_close(close_prices):
    yearly_avg_close = close_prices.groupby(close_prices.index.year).mean()
    return yearly_avg_close

# Function to get tickers based on category
def get_category_tickers(category):
    if category in data:
        return data[category]
    else:
        return "Category not found."

# Function to get stock data based on category
def find_stock_data(category):
    tickers = get_category_tickers(category)
    for ticker in tickers:
        # Extract close prices for specific dates from Yahoo Finance
        close_prices = extract_close_prices(ticker)

        # Calculate yearly average close price if available
        if close_prices is not None:
            yearly_avg_close = calculate_yearly_avg_close(close_prices)
            if not yearly_avg_close.empty:
                if len(yearly_avg_close) == 14:
                    print(f"Yearly average close prices for {ticker}:")
                    print(yearly_avg_close)
                else:
                    print(f"Yearly average close prices for {ticker}:")
                    print(yearly_avg_close)

# Load the JSON file
with open('archive/catFun.json') as f:
    data = json.load(f)


# with open('categories.txt', 'r') as file:
#     lines = file.readlines()

# for line in lines:
#     category = line

while(1):
    category = input("Enter category:")
    find_stock_data(category)
