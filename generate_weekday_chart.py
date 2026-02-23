import pandas as pd
import plotly.graph_objects as go
import os

def create_weekday_chart():
    csv_path = 'market_data.csv'
    output_path = 'weekday_chart.html'
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
        
    print("Loading data for weekday chart...")
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

    # Drop rows without prices
    df_clean = df.dropna(subset=[target_col]).copy()
    
    # Make date timezone-naive and normalize to just the calendar date
    df_clean['Date'] = df_clean['Date'].dt.tz_localize(None).dt.normalize()
    
    # Drop duplicates if any, keeping the latest timestamp for a day
    df_clean = df_clean.drop_duplicates(subset=['Date'], keep='last')
    
    # Set Date as index and resample to daily frequency (including weekends/holidays)
    # Using forward fill so holidays retain the previous close price (0% return)
    df_clean = df_clean.set_index('Date').resample('D').ffill()
    
    # Calculate strictly 1-calendar-day return
    df_clean['Daily_Return'] = df_clean[target_col].pct_change() * 100
    
    # Extract day of the week (0=Monday, 6=Sunday)
    df_clean['Weekday_Num'] = df_clean.index.dayofweek
    df_clean['Weekday'] = df_clean.index.day_name()
    
    # Drop first row which has NaN return
    df_clean = df_clean.dropna(subset=['Daily_Return']).copy()
    
    df_clean['Year'] = df_clean.index.year
    start_year = df_clean['Year'].min()
    end_year = df_clean['Year'].max()
    
    current_year = 2026
    ranges = [
        ("All Time", start_year),
        ("Last 50 Years", current_year - 50),
        ("Last 30 Years", current_year - 30),
        ("Last 20 Years", current_year - 20),
        ("Last 10 Years", current_year - 10)
    ]

    fig = go.Figure()
    
    # Pre-calculate data for each range and add a bar trace
    for i, (label, cutoff_year) in enumerate(ranges):
        actual_cutoff = max(cutoff_year, start_year)
        
        df_range = df_clean[df_clean['Year'] >= actual_cutoff]
        
        # We also want to drop weekends since they will just show 0% and dilute the main bars
        df_range_tradable = df_range[~df_range['Weekday_Num'].isin([5, 6])]
        
        # Group by weekday and calculate stats for this range
        weekday_stats = df_range_tradable.groupby(['Weekday_Num', 'Weekday']).agg(
            Avg_Return=('Daily_Return', 'mean'),
            Hit_Rate=('Daily_Return', lambda x: (x > 0).mean() * 100),
            Count=('Daily_Return', 'count')
        ).reset_index()
        
        weekday_stats = weekday_stats.sort_values('Weekday_Num')
        weekday_stats = weekday_stats[weekday_stats['Count'] > 50] # lowered threshold slightly for shorter ranges
        
        colors = ['#00CC96' if val >= 0 else '#EF553B' for val in weekday_stats['Avg_Return']]
        
        visible = (i == 0) # Only the first one is visible by default
        
        fig.add_trace(go.Bar(
            x=weekday_stats['Weekday'],
            y=weekday_stats['Avg_Return'],
            marker_color=colors,
            text=weekday_stats['Avg_Return'].apply(lambda x: f"{x:+.3f}%"),
            textposition='auto',
            hoverinfo='text',
            hovertemplate=(
                "<b>%{x}</b><br>" +
                "Avg Return: %{y:+.3f}%<br>" +
                "Positive Days (Hit Rate): %{customdata[0]:.1f}%<br>" +
                "Total Trading Days: %{customdata[1]:,}<extra></extra>"
            ),
            customdata=weekday_stats[['Hit_Rate', 'Count']].values,
            visible=visible,
            name=label
        ))

    # Create buttons for updatemenus
    buttons = []
    for i, (label, cutoff_year) in enumerate(ranges):
        actual_cutoff = max(cutoff_year, start_year)
        visibility = [False] * len(ranges)
        visibility[i] = True
        
        buttons.append(dict(
            label=f"{label} ({actual_cutoff} - {end_year})",
            method="update",
            args=[
                {"visible": visibility},
                {"title": f"S&P 500 Average Daily Return by Day of the Week<br><sup>Data Period: {actual_cutoff} - {end_year} | Measured close-to-close</sup>"}
            ]
        ))
        
    fig.update_layout(
        updatemenus=[
            dict(
                type="dropdown",
                direction="down",
                x=0.01,
                xanchor="left",
                y=1.12,
                yanchor="bottom",
                active=0,
                showactive=True,
                buttons=buttons,
                bgcolor="#333",
                font=dict(color="white")
            )
        ],
        title=f"S&P 500 Average Daily Return by Day of the Week<br><sup>Data Period: {start_year} - {end_year} | Measured close-to-close</sup>",
        xaxis_title="Day of the Week",
        yaxis_title="Average Daily Return (%)",
        template='plotly_dark',
        yaxis=dict(tickformat='.3f'),
        showlegend=False
    )
    
    fig.write_html(output_path)
    print(f"Weekday chart successfully saved to {output_path}")

if __name__ == '__main__':
    create_weekday_chart()
