import pandas as pd
import plotly.graph_objects as go
import os

def create_chart():
    csv_path = 'market_data.csv'
    output_path = 'absolute_return_distribution_chart.html'
    
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
    
    # Calculate absolute returns
    df_clean['Abs_Return'] = df_clean['Daily_Return'].abs()
    
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
    
    categories = [
        " < -3.00%",
        "-3.00% to -2.00%",
        "-2.00% to -1.50%",
        "-1.50% to -1.00%",
        "-1.00% to -0.75%",
        "-0.75% to -0.50%",
        "-0.50% to  0.00%",
        " 0.00% to  0.50%",
        " 0.50% to  0.75%",
        " 0.75% to  1.00%",
        " 1.00% to  1.50%",
        " 1.50% to  2.00%",
        " 2.00% to  3.00%",
        " > 3.00%"
    ]
    fig = go.Figure()
    period_buttons = []
    
    for i, (label, start_yr) in enumerate(ranges):
        actual_start_yr = max(start_yr, start_year_data)
        df_range = df_clean[df_clean['Year'] >= actual_start_yr]
        
        r = df_range['Daily_Return']
        t = len(r)
        
        counts = [
            (r < -3.0).sum(),
            ((r >= -3.0) & (r < -2.0)).sum(),
            ((r >= -2.0) & (r < -1.5)).sum(),
            ((r >= -1.5) & (r < -1.0)).sum(),
            ((r >= -1.0) & (r < -0.75)).sum(),
            ((r >= -0.75) & (r < -0.5)).sum(),
            ((r >= -0.5) & (r < 0.0)).sum(),
            ((r >= 0.0) & (r <= 0.5)).sum(),
            ((r > 0.5) & (r <= 0.75)).sum(),
            ((r > 0.75) & (r <= 1.0)).sum(),
            ((r > 1.0) & (r <= 1.5)).sum(),
            ((r > 1.5) & (r <= 2.0)).sum(),
            ((r > 2.0) & (r <= 3.0)).sum(),
            (r > 3.0).sum()
        ]
        
        percentages = [c / t * 100 for c in counts]
        
        visible = (i == 0) # Default to 'All Time'
        
        marker_colors = ['#EF553B'] * 7 + ['#00CC96'] * 7
        
        fig.add_trace(go.Bar(
            x=categories,
            y=percentages,
            name=f'{label}',
            visible=visible,
            marker_color=marker_colors,
            opacity=0.9,
            text=[f"{p:.2f}%<br>({c})" for p, c in zip(percentages, counts)],
            textposition='auto',
            hovertemplate="Range: %{x}<br>Percentage: %{y:.2f}%<extra></extra>"
        ))
        
        visibility = [False] * len(ranges)
        visibility[i] = True
        
        title_str = f'S&P 500 Daily Return Binned Distribution ({actual_start_yr} - {years_sorted[-1]})'
        
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
        xaxis_title='Daily Return Range (%)',
        yaxis_title='Frequency (%)',
        template='plotly_dark',
        showlegend=False
    )
    
    fig.write_html(output_path)
    print(f"Chart successfully saved to {output_path}")

if __name__ == '__main__':
    create_chart()
