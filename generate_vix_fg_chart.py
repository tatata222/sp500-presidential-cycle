import pandas as pd
import requests
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def create_vix_fg_chart():
    output_path = 'vix_fg_chart.html'
    
    print("Fetching VIX data...")
    try:
        vix = yf.download('^VIX', period='max')
        if isinstance(vix.columns, pd.MultiIndex):
            # Try to correctly select the Close column
            if ('Close', '^VIX') in vix.columns:
                vix_close = vix[('Close', '^VIX')]
            else:
                vix_close = vix['Close']
        else:
            vix_close = vix['Close']
            
        df_vix = pd.DataFrame({'VIX': vix_close})
        df_vix.index = pd.to_datetime(df_vix.index, utc=True).normalize()
    except Exception as e:
        print(f"Failed to fetch VIX: {e}")
        return

    print("Fetching CNN Fear & Greed Index data...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://edition.cnn.com/markets/fear-and-greed'
        }
        r = requests.get('https://production.dataviz.cnn.io/index/fearandgreed/graphdata', headers=headers)
        r.raise_for_status()
        d = r.json()
        hist = d.get('fear_and_greed_historical', {}).get('data', [])
        
        if hist:
            df_fg = pd.DataFrame(hist)
            # x is timestamp in ms
            df_fg['Date'] = pd.to_datetime(df_fg['x'], unit='ms', utc=True).dt.normalize()
            df_fg = df_fg.rename(columns={'y': 'FearGreed'})
            df_fg = df_fg[['Date', 'FearGreed']].drop_duplicates('Date').set_index('Date')
        else:
            df_fg = pd.DataFrame(columns=['Date', 'FearGreed']).set_index('Date')
            print("Warning: Fear & Greed historical data is empty.")
    except Exception as e:
        print(f"Failed to fetch Fear & Greed: {e}")
        df_fg = pd.DataFrame(columns=['Date', 'FearGreed']).set_index('Date')

    # Merge data
    df = pd.merge(df_vix, df_fg, left_index=True, right_index=True, how='outer')
    df = df.sort_index().reset_index()
    # rename index column if created
    if 'index' in df.columns:
        df = df.rename(columns={'index': 'Date'})

    df = df.dropna(subset=['VIX', 'FearGreed'], how='all')

    print("Generating Chart...")
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['VIX'], name="VIX", line=dict(color='#EF553B')),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['FearGreed'], name="Fear & Greed Index", line=dict(color='#00CC96')),
        secondary_y=True,
    )

    fig.update_layout(
        title="VIX & CNN Fear & Greed Index (恐怖と強欲指数)",
        xaxis_title="Date",
        template='plotly_dark',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Note: Fear & Greed Index goes 0 to 100
    fig.update_yaxes(title_text="VIX", secondary_y=False, rangemode='tozero')
    fig.update_yaxes(title_text="Fear & Greed Index (0-100)", secondary_y=True, range=[0, 100], gridcolor='#333333')

    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=5, label="5y", step="year", stepmode="backward"),
                dict(count=10, label="10y", step="year", stepmode="backward"),
                dict(step="all")
            ]),
            bgcolor="#333",
            font=dict(color="white")
        )
    )

    fig.write_html(output_path)
    print(f"Chart successfully saved to {output_path}")

if __name__ == '__main__':
    create_vix_fg_chart()
