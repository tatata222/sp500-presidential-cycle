import yfinance as yf
import pandas as pd
import os

def fetch_and_merge():
    csv_path = 'market_data.csv'
    
    print("Loading existing data...")
    if os.path.exists(csv_path):
        df_existing = pd.read_csv(csv_path)
        df_existing['Date'] = pd.to_datetime(df_existing['Date'], utc=True)
        if 'Nikkei 225' in df_existing.columns:
            df_existing = df_existing.drop(columns=['Nikkei 225'])
        if 'TOPIX' in df_existing.columns:
            df_existing = df_existing.drop(columns=['TOPIX'])
    else:
        print("market_data.csv not found.")
        return

    print("Fetching Nikkei 225 (^N225)...")
    n225 = yf.Ticker('^N225').history(period="max")
    n225_close = n225[['Close']].rename(columns={'Close': 'Nikkei 225'})
    n225_close.index = pd.to_datetime(n225_close.index, utc=True).normalize()
    
    print("Fetching TOPIX ETF (1306.T)...")
    topix = yf.Ticker('1306.T').history(period="max")
    topix_close = topix[['Close']].rename(columns={'Close': 'TOPIX'})
    topix_close.index = pd.to_datetime(topix_close.index, utc=True).normalize()

    # Combine new data
    new_data = n225_close.join(topix_close, how='outer')
    new_data = new_data.reset_index().rename(columns={'index': 'Date'})
    new_data['Date'] = new_data['Date'].dt.normalize()
    
    # Merge with existing data
    df_existing['Date'] = df_existing['Date'].dt.normalize()
    
    # Standardize column naming: Date, S&P 500, NASDAQ 100, US 10-Year Treasury Yield, Nikkei 225, TOPIX
    combined = pd.merge(df_existing, new_data, on='Date', how='outer')
    
    # Remove duplicates
    combined = combined.groupby('Date').last().reset_index()
    combined = combined.sort_values('Date').reset_index(drop=True)
    
    combined.to_csv(csv_path, index=False)
    print("Merged Nikkei 225 and TOPIX data into market_data.csv")

if __name__ == '__main__':
    fetch_and_merge()
