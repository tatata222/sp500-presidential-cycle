import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import os

def generate_vix_list_table():
    output_path = 'vix_sp500_returns_table.html'
    
    print("Fetching VIX and S&P 500 data...")
    tickers = ['^VIX', '^GSPC']
    data = yf.download(tickers, period='max')
    
    if isinstance(data.columns, pd.MultiIndex):
        vix = data['Close']['^VIX']
        sp500 = data['Close']['^GSPC']
    else:
        vix = data['Close']
        sp500 = data['Close']
        
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
            '1_Week': date + pd.Timedelta(days=7),
            '1_Month': date + pd.DateOffset(months=1),
            '3_Month': date + pd.DateOffset(months=3),
            '6_Month': date + pd.DateOffset(months=6),
            '1_Year': date + pd.DateOffset(years=1)
        }
        
        row = {
            'Date': date_str, 
            'VIX': df.loc[date, 'VIX'], 
            'SP500': price_0,
            'Ret_1W': None,
            'Ret_1M': None,
            'Ret_3M': None,
            'Ret_6M': None,
            'Ret_1Y': None
        }
        
        mapping = {
            '1_Week': 'Ret_1W',
            '1_Month': 'Ret_1M',
            '3_Month': 'Ret_3M',
            '6_Month': 'Ret_6M',
            '1_Year': 'Ret_1Y'
        }
        
        for label, t_date in target_dates.items():
            future_data = df[df.index >= t_date]
            if not future_data.empty:
                first_future_date = future_data.index[0]
                price_future = future_data.loc[first_future_date, 'SP500']
                ret = (price_future - price_0) / price_0 * 100
                row[mapping[label]] = ret
                
        results.append(row)
        
    res_df = pd.DataFrame(results)
    
    # Formatting for Plotly Table
    dates = res_df['Date']
    vix_vals = [f"{v:.2f}" for v in res_df['VIX']]
    sp500_vals = [f"{v:.2f}" for v in res_df['SP500']]
    
    def format_ret(val):
        if pd.isna(val):
            return "N/A"
        return f"{val:+.2f}%"
        
    def get_color(val):
        if pd.isna(val):
            return 'white'
        if val < 0:
            return '#ff4444'
        elif val >= 5:
            return '#00ff00'
        else:
            return 'white'

    ret_1w_str = [format_ret(v) for v in res_df['Ret_1W']]
    ret_1m_str = [format_ret(v) for v in res_df['Ret_1M']]
    ret_3m_str = [format_ret(v) for v in res_df['Ret_3M']]
    ret_6m_str = [format_ret(v) for v in res_df['Ret_6M']]
    ret_1y_str = [format_ret(v) for v in res_df['Ret_1Y']]
    
    font_colors = [
        ['white'] * len(res_df),
        ['white'] * len(res_df),
        ['white'] * len(res_df),
        [get_color(v) for v in res_df['Ret_1W']],
        [get_color(v) for v in res_df['Ret_1M']],
        [get_color(v) for v in res_df['Ret_3M']],
        [get_color(v) for v in res_df['Ret_6M']],
        [get_color(v) for v in res_df['Ret_1Y']],
    ]
    
    fill_colors = [['#2a2a2a'] * len(res_df) for _ in range(8)]
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Date', 'VIX', 'S&P 500', '1 Week Later', '1 Month Later', '3 Months Later', '6 Months Later', '1 Year Later'],
            fill_color='#111111',
            align='center',
            font=dict(color='white', size=14),
            height=40
        ),
        cells=dict(
            values=[
                dates, 
                vix_vals, 
                sp500_vals, 
                ret_1w_str,
                ret_1m_str,
                ret_3m_str,
                ret_6m_str,
                ret_1y_str
            ],
            fill_color=fill_colors,
            font=dict(color=font_colors, size=13),
            align=['center', 'right', 'right', 'right', 'right', 'right', 'right', 'right'],
            height=30
        )
    )])

    num_events = len(res_df)
    
    fig.update_layout(
        title=f"S&P 500 Forward Returns after VIX crosses above 30<br><sup>Total Occurrences since 1990: {num_events} times</sup>",
        template='plotly_dark',
        margin=dict(l=20, r=20, t=80, b=20)
    )

    fig.write_html(output_path)
    print(f"VIX table successfully saved to {output_path}")

if __name__ == "__main__":
    generate_vix_list_table()
