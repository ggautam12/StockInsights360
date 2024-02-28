import pandas as pd
from sqlalchemy import create_engine
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import mysql.connector
import os
import plotly.express as px
import plotly.io as pio
from datetime import datetime

# Database connection details
db_username = 'Gautam'
db_password = 'Great$43111'
db_host = '127.0.0.1'
db_port = '3306'
db_name = 'Stocks.io'

# Establishing the database connection
engine = create_engine(f'mysql+mysqlconnector://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}')

# Directory for saving plots
plot_directory = r'C:\Users\Gautam Batman\stock_plots'
if not os.path.exists(plot_directory):
    os.makedirs(plot_directory)

# Fetching and preparing the historical data
historical_data = pd.DataFrame()
for year in range(2014, 2025):
    table_name = f'stocks_({year},)'  # Adjusted table name format
    query = f"SELECT * FROM `{table_name}`"
    df_year = pd.read_sql(query, engine)
    df_year['Year'] = year
    historical_data = pd.concat([historical_data, df_year])

# Convert 'Date' column to datetime if not already
historical_data['Date'] = pd.to_datetime(historical_data['Date'])

# Feature engineering
historical_data['MA10'] = historical_data.groupby('Ticker')['Close'].transform(lambda x: x.rolling(window=10).mean())
historical_data['MA30'] = historical_data.groupby('Ticker')['Close'].transform(lambda x: x.rolling(window=30).mean())
historical_data['Volatility'] = historical_data.groupby('Ticker')['Close'].transform(
    lambda x: x.rolling(window=30).std())
historical_data['Daily_Change'] = historical_data.groupby('Ticker')['Close'].transform(lambda x: x.pct_change())
historical_data.dropna(inplace=True)

features = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'MA10', 'MA30', 'Volatility', 'Daily_Change']
X = historical_data[features]
y = historical_data['Close']

# Data scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Model training
model = XGBRegressor(n_estimators=100, objective='reg:squarederror')
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)

# Prediction and selection of top 5 stocks
recent_data = historical_data[historical_data['Year'] >= 2023]
X_recent = scaler.transform(recent_data[features])
recent_data['Predicted_Close'] = model.predict(X_recent)
# Updated calculation for Predicted_Growth based on the new formula
recent_data['Predicted_Growth'] = ((recent_data['Close'] / recent_data['Open']) * 100)
top_5_stocks = recent_data.sort_values(by='Predicted_Growth', ascending=False).drop_duplicates(subset=['Ticker'], keep='first').head(5)

# Static plots for top 5 stocks
for ticker in top_5_stocks['Ticker']:
    data = recent_data[recent_data['Ticker'] == ticker]
    plt.figure(figsize=(10, 6))
    plt.plot(data['Date'], data['Close'], label='Actual Close')
    plt.plot(data['Date'], data['Predicted_Close'], linestyle='--', label='Predicted Close')
    growth = data.iloc[-1]['Predicted_Growth']
    plt.title(f"{ticker}: Actual vs. Predicted Close (Growth: {growth:.2f}%)")
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    file_path = os.path.join(plot_directory, f"{ticker}_growth.png")
    plt.savefig(file_path)
    plt.close()

# Interactive visualization for a specified ticker
ticker_input = input("Enter a ticker for interactive visualization (e.g., AAPL): ")
if ticker_input in historical_data['Ticker'].values:
    data_for_plot = recent_data[recent_data['Ticker'] == ticker_input]
    fig = px.line(data_for_plot, x='Date', y=['Close', 'Predicted_Close'],
                  labels={'value': 'Stock Price', 'variable': 'Type'}, title=f"{ticker_input}: Stock Price Prediction")
    interactive_plot_path = os.path.join(plot_directory, f"{ticker_input}_interactive.html")
    pio.write_html(fig, file=interactive_plot_path)
    print(f"Interactive plot for {ticker_input} saved.")
else:
    print("Ticker not found.")


# Function to insert plot metadata into MySQL database
def insert_plot_metadata_to_db(ticker, filepath):
    conn = mysql.connector.connect(user=db_username, password=db_password, host=db_host, database=db_name)
    cursor = conn.cursor()
    query = "REPLACE INTO stock_plot_paths (ticker, plot_path) VALUES (%s, %s)"
    cursor.execute(query, (ticker, filepath))
    conn.commit()
    cursor.close()
    conn.close()


# Continue with the function for processing and plotting top 2 tickers by growth for each year as previously defined

# Function to calculate and plot top 2 tickers by growth for each year
def process_and_plot_yearly_top_2_growth(year):
    # Filter data for the specified year
    data = historical_data[historical_data['Year'] == year]

    # Calculate monthly average close price and monthly growth
    data['Month'] = data['Date'].dt.month
    monthly_avg = data.groupby(['Ticker', 'Month'])['Close'].mean().reset_index()
    monthly_avg['Monthly Growth'] = monthly_avg.groupby('Ticker')['Close'].pct_change()

    # Calculate total annual growth for each ticker
    annual_growth = monthly_avg.groupby('Ticker')['Monthly Growth'].sum().reset_index()

    # Identify the top 2 tickers by annual growth
    top_2_tickers = annual_growth.nlargest(2, 'Monthly Growth')['Ticker']

    # Generate plot for the top 2 tickers
    plt.figure(figsize=(12, 6))
    for ticker in top_2_tickers:
        ticker_data = monthly_avg[monthly_avg['Ticker'] == ticker]
        plt.plot(ticker_data['Month'], ticker_data['Monthly Growth'] * 100,
                 label=f"{ticker} ({annual_growth[annual_growth['Ticker'] == ticker]['Monthly Growth'].iloc[0] * 100:.2f}%)")

    plt.title(f"Top 2 Stocks by Growth in {year}")
    plt.xlabel("Month")
    plt.ylabel("Growth Percentage")
    plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plt.legend()
    plt.grid(True)

    file_path = os.path.join(plot_directory, f"Top_2_Growth_{year}.png")
    plt.savefig(file_path)
    plt.close()

    # Insert plot metadata into database
    insert_plot_metadata_to_db(f"TOP2_{year}", file_path)
    print(f"Plot for the top 2 stocks by growth in {year} saved.")


# Process and plot yearly top 2 tickers by growth for each available year
for year in range(2014, 2025):
    try:
        process_and_plot_yearly_top_2_growth(year)
    except Exception as e:
        print(f"Could not process data for year {year}: {e}")
