import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def create_jp_chart():
    csv_path = 'market_data.csv'
    output_path = 'jp_market_chart.html'
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
        
    print("Loading Japanese market data...")
    try:
        df = pd.read_csv(csv_path)
        df['Date'] = pd.to_datetime(df['Date'], utc=True)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Check if necessary columns exist
    if 'Nikkei 225' not in df.columns or 'TOPIX' not in df.columns:
        print("Required columns (Nikkei 225, TOPIX) not found.")
        return

    # Remove rows where both Nikkei 225 and TOPIX are NaN
    df_clean = df.dropna(subset=['Nikkei 225', 'TOPIX'], how='all').copy()
    df_clean = df_clean.sort_values('Date')
    
    # We will just plot both on the same graph but with 2 y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=df_clean['Date'], y=df_clean['Nikkei 225'], name="Nikkei 225", line=dict(color='#00CC96')),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(x=df_clean['Date'], y=df_clean['TOPIX'], name="TOPIX ETF (1306.T)", line=dict(color='#AB63FA')),
        secondary_y=True,
    )

    fig.update_layout(
        title="日本株市場の過去推移 (日経平均 vs TOPIX)",
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
    
    fig.update_yaxes(title_text="Nikkei 225", secondary_y=False)
    fig.update_yaxes(title_text="TOPIX ETF (1306.T)", secondary_y=True)
    
    # Add Range Slider
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
    print(f"Japanese Market Chart successfully saved to {output_path}")

if __name__ == '__main__':
    create_jp_chart()
