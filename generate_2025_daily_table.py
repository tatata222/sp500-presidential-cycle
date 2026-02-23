import pandas as pd
import plotly.graph_objects as go
import os

def create_2025_daily_table():
    csv_path = 'market_data.csv'
    output_path = 'daily_2025_table.html'
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
        
    print("Loading data for 2025 daily table...")
    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'], utc=True)
    
    target_col = 'S&P 500'
    df_clean = df.dropna(subset=[target_col]).copy()
    
    # Sort strictly by date first
    df_clean = df_clean.sort_values('Date').reset_index(drop=True)
    
    # Calculate daily return across the WHOLE dataset FIRST,
    # so that the very first day of 2025 uses the last day of 2024 for its calculation.
    df_clean['Daily_Return'] = df_clean[target_col].pct_change() * 100
    df_clean['Weekday'] = df_clean['Date'].dt.day_name()
    df_clean['Date_Str'] = df_clean['Date'].dt.strftime('%Y-%m-%d')
    df_clean['Year'] = df_clean['Date'].dt.year
    
    # Filter for the year 2025 exclusively
    df_2025 = df_clean[df_clean['Year'] == 2025].copy()
    
    # If there are NaN daily returns (shouldn't be, unless 2025 is the very first year in the dataset), drop them or fill 0
    df_2025['Daily_Return'] = df_2025['Daily_Return'].fillna(0)
    
    if df_2025.empty:
        print("No data found for the year 2025.")
        return
        
    print(f"Found {len(df_2025)} trading days in 2025. Generating table...")
    
    # Cell colors: background for negative/positive
    cell_colors = [
        ['#2a2a2a'] * len(df_2025), # Date
        ['#2a2a2a'] * len(df_2025), # Weekday
        ['#2a2a2a'] * len(df_2025), # Price
        ['#00441b' if val >= 0 else '#67000d' for val in df_2025['Daily_Return']] # Return
    ]
    
    font_colors = [
        ['white'] * len(df_2025),
        ['white'] * len(df_2025),
        ['white'] * len(df_2025),
        ['#00ff00' if val >= 0 else '#ff4444' for val in df_2025['Daily_Return']] # Return text color
    ]
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Date', 'Day of Week', 'S&P 500 Close', 'Daily Return (%)'],
            fill_color='#111111',
            align='center',
            font=dict(color='white', size=14),
            height=40
        ),
        cells=dict(
            values=[
                df_2025['Date_Str'], 
                df_2025['Weekday'], 
                df_2025[target_col], 
                df_2025['Daily_Return']
            ],
            fill_color=cell_colors,
            font=dict(color=font_colors, size=13),
            align=['center', 'center', 'right', 'right'],
            height=30,
            format=["", "", ".2f", "+.3f"]
        )
    )])

    # Summary stats for the title
    avg_return = df_2025['Daily_Return'].mean()
    positive_days = (df_2025['Daily_Return'] > 0).sum()
    total_days = len(df_2025)
    win_rate = (positive_days / total_days) * 100 if total_days > 0 else 0
    
    fig.update_layout(
        title=f"S&P 500 Daily Returns for 2025<br><sup>Total Trading Days: {total_days} | Average Daily Return: {avg_return:.3f}% | Win Rate: {win_rate:.1f}% ({positive_days}/{total_days})</sup>",
        template='plotly_dark',
        margin=dict(l=20, r=20, t=80, b=20)
    )

    fig.write_html(output_path)
    print(f"Daily 2025 table successfully saved to {output_path}")

if __name__ == '__main__':
    create_2025_daily_table()
