import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine, MetaData, Table, Column, String, Float, Date, Integer

# Assuming 'Ticker' and 'Date' columns exist in your CSV
csv_file_path = "C:/Users/Gautam Batman/Downloads/SP500.csv"
df = pd.read_csv(csv_file_path)
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year

# Database connection - make sure the database 'stocks.io' exists
engine = create_engine('mysql+mysqlconnector://Gautam:Great$43111@127.0.0.1:3306/stocks.io')
metadata = MetaData()

# Create and populate tables for each year
for year, group in df.groupby(['Year']):
    table_name = f"stocks_{year}"

    # Define the table structure
    table = Table(table_name, metadata,
                  Column('Date', Date),
                  Column('Ticker', String(10)),
                  Column('Open', Float),
                  Column('High', Float),
                  Column('Low', Float),
                  Column('Close', Float),
                  Column('Adj_Close', Float),
                  Column('Volume', Integer),
                  extend_existing=True)

    # Create the table in the database
    metadata.create_all(engine)

    # Insert the data into the table
    group.to_sql(name=table_name, con=engine, if_exists='replace', index=False)

print("Data successfully inserted into MySQL database grouped by year.")
