import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
import numpy as np

# Function to calculate On-balance Volume (OBV)
def calculate_obv(data):
    OBV = [0]
    for i in range(1, len(data)):
        if data['Close'].iloc[i] > data['Close'].iloc[i - 1]:
            OBV.append(OBV[-1] + data['Volume'].iloc[i])
        elif data['Close'].iloc[i] < data['Close'].iloc[i - 1]:
            OBV.append(OBV[-1] - data['Volume'].iloc[i])
        else:
            OBV.append(OBV[-1])
    return pd.Series(OBV, index=data.index)

# Function to calculate Accumulation/Distribution Line (ADL)
def calculate_ad(data):
    clv = ((data['Close'] - data['Low']) - (data['High'] - data['Close'])) / (data['High'] - data['Low']).replace(0, np.nan)
    clv.fillna(0, inplace=True)
    AD = clv * data['Volume']
    return AD.cumsum()

# Function to calculate Moving Average Convergence Divergence (MACD)
def calculate_macd(data):
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

# Function to calculate Relative Strength Index (RSI)
def calculate_rsi(data, periods=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    RS = gain / loss
    RSI = 100 - (100 / (1 + RS))
    return RSI

# Function to fetch the industry of a ticker using yfinance
def fetch_industry(ticker):
    try:
        stock = yf.Ticker(ticker)
        industry = stock.info.get('industry', 'Unknown')
        return industry
    except Exception as e:
        print(f"Error fetching industry for {ticker}: {e}")
        return 'Unknown'

# Function to create a database engine
def get_db_engine(user, password, host, port, database):
    connection_string = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)
    return engine

# Main script
if __name__ == "__main__":
    csv_file_path = "C:/Users/Gautam Batman/Downloads/DATA.csv"
    df = pd.read_csv(csv_file_path)

    # Define the start and end dates for data fetching
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.DateOffset(years=10)

    all_data = pd.DataFrame()

    for index, row in df.iterrows():
        ticker = row['TICKER']
        print(f"Fetching data for {ticker}")

        try:
            stock_data = yf.download(ticker, start=start_date, end=end_date)
            if not stock_data.empty:
                stock_data['OBV'] = calculate_obv(stock_data)
                stock_data['AD'] = calculate_ad(stock_data)
                stock_data['MACD'], stock_data['Signal'] = calculate_macd(stock_data)
                stock_data['RSI'] = calculate_rsi(stock_data)

                # Fetch the industry and add it to the stock_data DataFrame
                stock_data['Industry'] = fetch_industry(ticker)

                stock_data['Ticker'] = ticker
                stock_data.reset_index(inplace=True, drop=False)  # Ensure 'Date' remains as a column
                all_data = pd.concat([all_data, stock_data])
            else:
                print(f"Data for {ticker} could not be downloaded.")
        except Exception as e:
            print(f"Failed to fetch data for {ticker}: {e}")

    # Save the combined DataFrame to a CSV file
    new_csv_file_path = "C:/Users/Gautam Batman/Downloads/SP500_with_Industry.csv"
    all_data.to_csv(new_csv_file_path, index=False)
    print(f"Data has been successfully written to {new_csv_file_path}")