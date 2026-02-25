import yfinance as yf
import pandas as pd
import os
import functools

def update_market_data():
    csv_path = 'market_data.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    print("Loading existing data...")
    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'], utc=True)

    symbols = {
        'S&P 500': '^GSPC',
        'NASDAQ 100': '^NDX',
        'US 10-Year Treasury Yield': '^TNX',
        'Nikkei 225': '^N225',
        'TOPIX': '1306.T'
    }

    dfs = []
    print("Fetching latest data from Yahoo Finance...")
    for name, ticker in symbols.items():
        try:
            # 最新の7日間分のデータを取得
            t_data = yf.download(ticker, period="7d")
            if t_data.empty:
                continue
                
            # 'Close'列だけを取り出してDataFrameにする
            if isinstance(t_data.columns, pd.MultiIndex):
                close_series = t_data['Close'][ticker]
            else:
                close_series = t_data['Close']
                
            temp = pd.DataFrame({name: close_series})
            # Ensure index is datetime with UTC. yfinance sometimes loses tz or returns weird format.
            temp.index = pd.to_datetime(temp.index, utc=True).normalize()
            # Drop duplicates in the API response just in case
            temp = temp.groupby(temp.index).last()
            
            dfs.append(temp)
        except Exception as e:
            print(f"Failed to fetch {ticker}: {e}")

    if dfs:
        # 新しいデータを日付でマージ
        new_data = functools.reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True, how='outer'), dfs)
        new_data = new_data.reset_index().rename(columns={'index': 'Date'})
        
        # 既存データと結合
        df['Date'] = df['Date'].dt.normalize()
        combined = pd.concat([df, new_data])
        
        # 時間表記のズレ（00:00と05:00等）を吸収するため、日付(カレンダー日)単位でグループ化し、各列の有効な最新の値を残す
        # これにより、一方がNaNの行が優先されてデータが消えるのを防ぎます
        combined = combined.groupby('Date').last().reset_index()
        
        # 整理して保存
        combined = combined.sort_values('Date').reset_index(drop=True)
        combined.to_csv(csv_path, index=False)
        print("Successfully updated market_data.csv with the latest prices.")
    else:
        print("No new data was fetched.")

if __name__ == '__main__':
    update_market_data()
