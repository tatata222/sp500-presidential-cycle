import pandas as pd
import plotly.graph_objects as go
import os
import numpy as np

def create_chart():
    csv_path = 'market_data.csv'
    output_path = 'daily_return_distribution_chart.html'
    
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
    target_col = 'S&P 500'
    if target_col not in df.columns:
        print(f"Column {target_col} not found in the CSV.")
        return

    df_clean = df.dropna(subset=[target_col]).copy()
    df_clean = df_clean.sort_values('Date')
    df_clean['Year'] = df_clean['Date'].dt.year
    
    df_clean['Daily_Return'] = df_clean[target_col].pct_change() * 100
    df_clean = df_clean.dropna(subset=['Daily_Return'])
    
    current_year = 2026
    years_sorted = sorted(df_clean['Year'].unique())
    start_year_data = years_sorted[0]
    
    ranges = [
        ("All Time", start_year_data),
        ("Last 50 Years", current_year - 50),
        ("Last 30 Years", current_year - 30),
        ("Last 20 Years", current_year - 20),
        ("Last 10 Years", current_year - 10),
        ("Last 5 Years", current_year - 5)
    ]
    
    fig = go.Figure()
    
    period_buttons = []
    
    for i, (label, start_yr) in enumerate(ranges):
        actual_start_yr = max(start_yr, start_year_data)
        df_range = df_clean[df_clean['Year'] >= actual_start_yr]
        
        visible = (i == 0) # Default to 'All Time'
        
        returns = df_range['Daily_Return']
        
        mean_r = returns.mean()
        median_r = returns.median()
        std_r = returns.std()
        
        p25 = returns.quantile(0.25)
        p75 = returns.quantile(0.75)
        p12_5 = returns.quantile(0.125)
        p87_5 = returns.quantile(0.875)
        
        cond_50 = (returns >= p25) & (returns <= p75)
        cond_75 = ((returns >= p12_5) & (returns < p25)) | ((returns > p75) & (returns <= p87_5))
        cond_other = (returns < p12_5) | (returns > p87_5)
        
        # 50% Range trace
        fig.add_trace(go.Histogram(
            x=returns[cond_50],
            name=f'50% Range',
            visible=visible,
            marker_color='#636EFA', # Blue
            opacity=0.9,
            xbins=dict(start=-10.0, end=10.0, size=0.1),
            hovertemplate="Return: %{x:.2f}%<br>Count: %{y}<extra></extra>"
        ))
        
        # 75% Range trace
        fig.add_trace(go.Histogram(
            x=returns[cond_75],
            name=f'75% Range',
            visible=visible,
            marker_color='#AB63FA', # Purple
            opacity=0.8,
            xbins=dict(start=-10.0, end=10.0, size=0.1),
            hovertemplate="Return: %{x:.2f}%<br>Count: %{y}<extra></extra>"
        ))

        # Other trace
        fig.add_trace(go.Histogram(
            x=returns[cond_other],
            name=f'Other',
            visible=visible,
            marker_color='#7F7F7F', # Gray
            opacity=0.5,
            xbins=dict(start=-10.0, end=10.0, size=0.1),
            hovertemplate="Return: %{x:.2f}%<br>Count: %{y}<extra></extra>"
        ))
        
        visibility = [False] * (len(ranges) * 3)
        visibility[i*3] = True
        visibility[i*3+1] = True
        visibility[i*3+2] = True
        
        title_str = f'S&P 500 Daily Return Distribution ({actual_start_yr} - {years_sorted[-1]})<br><sup>Mean: {mean_r:.3f}% | Median: {median_r:.3f}% | Std Dev: {std_r:.3f}% | 50% Range: {p25:.2f}% to {p75:.2f}% | 75% Range: {p12_5:.2f}% to {p87_5:.2f}%</sup>'
        
        period_buttons.append(dict(
            label=f"{label} ({actual_start_yr} - {years_sorted[-1]})",
            method="update",
            args=[
                {"visible": visibility},
                {"title": title_str}
            ]
        ))
        
        if i == 0:
            default_title = title_str

    fig.update_layout(
        updatemenus=[
            dict(
                type="dropdown",
                direction="down",
                x=0.01,
                xanchor="left",
                y=1.15,
                yanchor="bottom",
                active=0, # Default is All Time
                showactive=True,
                buttons=period_buttons,
                bgcolor="#333",
                font=dict(color="white")
            )
        ],
        title=default_title,
        xaxis_title='Daily Return (%)',
        yaxis_title='Frequency (Number of Days)',
        template='plotly_dark',
        bargap=0.1,
        barmode='stack',
        xaxis=dict(range=[-5, 5], dtick=0.5),
        showlegend=True
    )
    
    fig.write_html(output_path)
    print(f"Chart successfully saved to {output_path}")

if __name__ == '__main__':
    create_chart()
