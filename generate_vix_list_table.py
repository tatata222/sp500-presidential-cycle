import pandas as pd
import yfinance as yf

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
                if isinstance(price_future, pd.Series):
                    price_future = price_future.iloc[0]
                if isinstance(price_0, pd.Series):
                    price_0 = price_0.iloc[0]
                ret = (price_future - price_0) / price_0 * 100
                row[mapping[label]] = float(ret)
                
        results.append(row)
        
    res_df = pd.DataFrame(results)
    
    def get_color_class(val):
        if pd.isna(val):
            return "white"
        if val < 0:
            return "red"
        if val >= 5:
            return "green"
        return "white"

    def format_val(val):
        if pd.isna(val):
            return "N/A"
        return f"{val:+.2f}%"

    rows_html = ""
    for _, row in res_df.iterrows():
        r_html = "<tr>"
        r_html += f"<td style='text-align: center;'>{row['Date']}</td>"
        r_html += f"<td>{row['VIX']:.2f}</td>"
        r_html += f"<td>{row['SP500']:.2f}</td>"
        for c in ['Ret_1W', 'Ret_1M', 'Ret_3M', 'Ret_6M', 'Ret_1Y']:
            val = row[c]
            c_class = get_color_class(val)
            txt = format_val(val)
            r_html += f"<td class='{c_class}'>{txt}</td>"
        r_html += "</tr>\n"
        rows_html += r_html
        
    num_events = len(res_df)
    
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            background-color: #111111;
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
        }}
        h2 {{
            text-align: center;
            margin-bottom: 5px;
            font-size: 20px;
        }}
        .subtitle {{
            text-align: center;
            color: #aaaaaa;
            font-size: 14px;
            margin-bottom: 20px;
            font-style: italic;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        th {{
            background-color: #222222;
            color: white;
            padding: 12px;
            text-align: right;
            border-bottom: 1px solid #444;
            position: sticky;
            top: 0;
            font-weight: bold;
        }}
        th:first-child {{
            text-align: center;
        }}
        td {{
            background-color: #2a2a2a;
            padding: 10px 12px;
            text-align: right;
            border-bottom: 1px solid #333;
        }}
        tr:hover td {{
            background-color: #333333;
        }}
        .red {{ color: #ff4444; }}
        .green {{ color: #00ff00; }}
        .white {{ color: white; }}
    </style>
</head>
<body>
    <h2>S&P 500 Forward Returns after VIX crosses above 30</h2>
    <div class="subtitle">Total Occurrences since 1990: {num_events} times</div>
    <table>
        <tr>
            <th>Date</th>
            <th>VIX</th>
            <th>S&P 500</th>
            <th>1 Week Later</th>
            <th>1 Month Later</th>
            <th>3 Months Later</th>
            <th>6 Months Later</th>
            <th>1 Year Later</th>
        </tr>
        {rows_html}
    </table>
</body>
</html>
"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
        
    print(f"VIX table successfully saved to {output_path}")

if __name__ == "__main__":
    generate_vix_list_table()
