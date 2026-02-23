import pandas as pd
import plotly.graph_objects as go
import os

def create_chart():
    csv_path = 'market_data.csv'
    output_path = 'yield_history_chart.html'
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
        
    print("Loading data...")
    try:
        df = pd.read_csv(csv_path)
        df['Date'] = pd.to_datetime(df['Date'], utc=True)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    print("Processing data...")
    target_col = 'US 10-Year Treasury Yield'
    if target_col not in df.columns:
        print(f"Column {target_col} not found in the CSV.")
        return

    df_clean = df.dropna(subset=[target_col]).copy()
    df_clean = df_clean.sort_values('Date')
    
    if df_clean.empty:
        print("No yield data available to plot.")
        return

    df_clean = df_clean.set_index('Date')
    weekly_data = df_clean[target_col].resample('W').mean().dropna()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=weekly_data.index,
        y=weekly_data.values,
        mode='lines',
        name='US 10-Year Yield',
        line=dict(color='#00CC96', width=2),
        hovertemplate="Date: %{x|%Y-%m-%d}<br>Yield: %{y:.3f}%<extra></extra>"
    ))

    fig.update_layout(
        title='US 10-Year Treasury Yield History (Weekly Average)',
        xaxis_title='Date',
        yaxis_title='Yield (%)',
        template='plotly_dark',
        hovermode='x unified',
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(count=5, label="5y", step="year", stepmode="backward"),
                    dict(count=10, label="10y", step="year", stepmode="backward"),
                    dict(label="All", step="all")
                ]),
                bgcolor="#333",
                activecolor="#555"
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    
    fig.write_html(output_path)
    print(f"Chart successfully saved to {output_path}")

if __name__ == '__main__':
    create_chart()
