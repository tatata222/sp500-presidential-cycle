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
    target_col_yield = 'US 10-Year Treasury Yield'
    target_col_sp500 = 'S&P 500'
    if target_col_yield not in df.columns or target_col_sp500 not in df.columns:
        print("Required columns not found in the CSV.")
        return

    # Drop rows where both yield and sp500 data is missing
    df_clean = df.dropna(subset=[target_col_yield, target_col_sp500], how='all').copy()
    df_clean = df_clean.sort_values('Date')
    
    if df_clean.empty:
        print("No data available to plot.")
        return

    df_clean = df_clean.set_index('Date')
    weekly_data = df_clean[[target_col_yield, target_col_sp500]].resample('W').mean().dropna(how='all')

    from plotly.subplots import make_subplots
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x=weekly_data.index,
        y=weekly_data[target_col_yield],
        mode='lines',
        name='US 10-Year Yield',
        line=dict(color='#00CC96', width=2),
        hovertemplate="Yield: %{y:.3f}%<extra></extra>"
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=weekly_data.index,
        y=weekly_data[target_col_sp500],
        mode='lines',
        name='S&P 500',
        line=dict(color='#636EFA', width=2),
        hovertemplate="S&P 500: %{y:.2f}<extra></extra>"
    ), secondary_y=True)

    fig.update_layout(
        title='US 10-Year Treasury Yield & S&P 500 History (Weekly Average)',
        xaxis_title='Date',
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
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Set y-axes titles
    fig.update_yaxes(title_text="Yield (%)", secondary_y=False)
    # Set secondary y-axis to logarithmic for better S&P 500 long term comparison
    fig.update_yaxes(title_text="S&P 500 (Log Scale)", type="log", secondary_y=True)
    
    fig.write_html(output_path)
    print(f"Chart successfully saved to {output_path}")

if __name__ == '__main__':
    create_chart()
