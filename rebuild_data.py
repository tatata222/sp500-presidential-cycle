import yfinance as yf
import pandas as pd
import functools

symbols = {
    'S&P 500': '^GSPC',
    'NASDAQ 100': '^NDX',
    'US 10-Year Treasury Yield': '^TNX'
}

dfs = []
for name, ticker in symbols.items():
    print(f"Fetching {name} ({ticker})...")
    t_data = yf.download(ticker, period="max")
    if t_data.empty:
        continue
    if isinstance(t_data.columns, pd.MultiIndex):
        close_series = t_data['Close'][ticker]
    else:
        close_series = t_data['Close']
    temp = pd.DataFrame({name: close_series})
    temp.index = pd.to_datetime(temp.index, utc=True)
    dfs.append(temp)

combined = functools.reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True, how='outer'), dfs)
combined = combined.reset_index().rename(columns={'index': 'Date'})

# Remove timezone if needed or save directly
combined = combined.sort_values('Date').reset_index(drop=True)

# Important: Don't just stringify and lose timezone later. Keep original format.
combined.to_csv('market_data.csv', index=False)
print("Rebuilt market_data.csv successfully!")
