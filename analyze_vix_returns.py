import yfinance as yf
import pandas as pd
import numpy as np
import datetime

def analyze_vix_returns():
    print("Fetching VIX and S&P 500 data...")
    
    # Fetch data
    tickers = ['^VIX', '^GSPC']
    data = yf.download(tickers, period='max')
    
    # Check if 'Close' is a MultiIndex or regular DataFrame
    if isinstance(data.columns, pd.MultiIndex):
        if ('Close', '^VIX') in data.columns:
            vix = data[('Close', '^VIX')]
            sp500 = data[('Close', '^GSPC')]
        else:
            vix = data['Close']['^VIX']
            sp500 = data['Close']['^GSPC']
    else:
        vix = data['Close']
        sp500 = data['Close'] # Just in case it downloaded weirdly
        
    df = pd.DataFrame({'VIX': vix, 'SP500': sp500})
    df = df.dropna()

    # Calculate returns (approximate trading days: 1W=5, 1M=21, 3M=63, 6M=126, 1Y=252)
    df['Return_1W'] = df['SP500'].shift(-5) / df['SP500'] - 1
    df['Return_1M'] = df['SP500'].shift(-21) / df['SP500'] - 1
    df['Return_3M'] = df['SP500'].shift(-63) / df['SP500'] - 1
    df['Return_6M'] = df['SP500'].shift(-126) / df['SP500'] - 1
    df['Return_1Y'] = df['SP500'].shift(-252) / df['SP500'] - 1

    # Win rate (percentage of positive returns)
    def print_stats(title, mask):
        filtered = df[mask]
        count = filtered.shape[0]
        
        # calculate mean return
        mean_1w = filtered['Return_1W'].mean() * 100
        mean_1m = filtered['Return_1M'].mean() * 100
        mean_3m = filtered['Return_3M'].mean() * 100
        mean_6m = filtered['Return_6M'].mean() * 100
        mean_1y = filtered['Return_1Y'].mean() * 100
        
        # calculate max return
        max_1y = filtered['Return_1Y'].max() * 100
        # calculate min return
        min_1y = filtered['Return_1Y'].min() * 100
        
        # calculate win rate
        win_1w = (filtered['Return_1W'] > 0).mean() * 100
        win_1m = (filtered['Return_1M'] > 0).mean() * 100
        win_3m = (filtered['Return_3M'] > 0).mean() * 100
        win_6m = (filtered['Return_6M'] > 0).mean() * 100
        win_1y = (filtered['Return_1Y'] > 0).mean() * 100

        print(f"\n{title}")
        print("-" * 50)
        print(f"対象日数（サンプル数）: {count} 日")
        print(f"1週間後 (約5営業日)   : 平均 {mean_1w:6.2f}% (勝率 {win_1w:5.1f}%)")
        print(f"1ヶ月後 (約21営業日)  : 平均 {mean_1m:6.2f}% (勝率 {win_1m:5.1f}%)")
        print(f"3ヶ月後 (約63営業日)  : 平均 {mean_3m:6.2f}% (勝率 {win_3m:5.1f}%)")
        print(f"6ヶ月後 (約126営業日) : 平均 {mean_6m:6.2f}% (勝率 {win_6m:5.1f}%)")
        print(f"1年後   (約252営業日) : 平均 {mean_1y:6.2f}% (勝率 {win_1y:5.1f}%)")
        print(f"  └ 1年後の最大リターン: {max_1y:6.2f}% / 最小リターン: {min_1y:6.2f}%")

    # Condition 1: All days where VIX >= 30
    mask_30_all = df['VIX'] >= 30
    print_stats("■ VIXが「30以上」で推移した全営業日のフォワード・リターン", mask_30_all)

    # Condition 2: VIX crossed above 30 (was < 30 on the previous day)
    df['VIX_prev'] = df['VIX'].shift(1)
    mask_30_cross = (df['VIX'] >= 30) & (df['VIX_prev'] < 30)
    print_stats("■ VIXが「30を上抜けた」当日のフォワード・リターン（連続期間をカウントせず初回のみ）", mask_30_cross)
    
    # Baseline for comparison:
    # Average return over any random day
    mask_all = pd.Series([True] * len(df), index=df.index)
    print_stats("■ 参考：S&P 500の全期間平均（いつでも投資した場合）", mask_all)

if __name__ == "__main__":
    analyze_vix_returns()
