import yfinance as yf
import pandas as pd
from datetime import timedelta

def analyze_vix_crosses():
    tickers = ['^VIX', '^GSPC']
    data = yf.download(tickers, period='max')
    
    if isinstance(data.columns, pd.MultiIndex):
        vix = data['Close']['^VIX']
        sp500 = data['Close']['^GSPC']
    else:
        vix = data['Close']
        sp500 = data['Close']
        
    # Ensure they are Series
    if isinstance(vix, pd.DataFrame):
        vix = vix.squeeze()
    if isinstance(sp500, pd.DataFrame):
        sp500 = sp500.squeeze()
        
    df = pd.DataFrame({'VIX': vix, 'SP500': sp500})
    df = df.dropna()

    df['VIX_prev'] = df['VIX'].shift(1)
    
    # 30を超えたタイミング（前日が30以下、当日が30より大きい）
    crosses = df[(df['VIX'] > 30) & (df['VIX_prev'] <= 30)]

    results = []
    
    for date in crosses.index:
        date_str = date.strftime('%Y-%m-%d')
        price_0 = df.loc[date, 'SP500']
        
        target_dates = {
            '1週間後': date + pd.Timedelta(days=7),
            '1ヶ月後': date + pd.DateOffset(months=1),
            '3ヶ月後': date + pd.DateOffset(months=3),
            '6ヶ月後': date + pd.DateOffset(months=6),
            '1年後': date + pd.DateOffset(years=1)
        }
        
        row = {'日付': date_str, 'VIX': f"{df.loc[date, 'VIX']:.2f}", '当時のS&P500': f"{price_0:.2f}"}
        
        for label, t_date in target_dates.items():
            future_data = df[df.index >= t_date]
            if not future_data.empty:
                first_future_date = future_data.index[0]
                price_future = future_data.loc[first_future_date, 'SP500']
                ret = (price_future - price_0) / price_0 * 100
                row[label] = f"{ret:+.2f}%"
            else:
                row[label] = "N/A"
                
        results.append(row)
        
    res_df = pd.DataFrame(results)
    print(res_df.to_markdown(index=False))

if __name__ == "__main__":
    analyze_vix_crosses()
