import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def create_chart():
    csv_path = 'market_data.csv'
    output_path = 'holiday_effect_chart.html'
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
        
    print("Loading data for holiday effect chart...")
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

    # Clean data
    df_clean = df.dropna(subset=[target_col]).copy()
    df_clean['Date'] = df_clean['Date'].dt.tz_localize(None).dt.normalize()
    df_clean = df_clean.drop_duplicates(subset=['Date'], keep='last')
    df_clean = df_clean.sort_values('Date').reset_index(drop=True)
    
    df_clean['Daily_Return'] = df_clean[target_col].pct_change() * 100
    df_clean = df_clean.dropna(subset=['Daily_Return']).copy()
    
    # Calculate days difference to find holidays
    df_clean['Next_Gap_Days'] = (df_clean['Date'].shift(-1) - df_clean['Date']).dt.days
    df_clean['Prev_Gap_Days'] = (df_clean['Date'] - df_clean['Date'].shift(1)).dt.days
    
    df_clean['Year'] = df_clean['Date'].dt.year
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

    fig = make_subplots(
        rows=1, cols=2, 
        subplot_titles=("休日 (1日以上の休み)", "連休 (2日以上の休み)"),
        horizontal_spacing=0.1
    )
    
    buttons = []
    
    for i, (label, cutoff_year) in enumerate(ranges):
        actual_cutoff = max(cutoff_year, start_year)
        df_range = df_clean[df_clean['Year'] >= actual_cutoff]
        
        # Holiday Logic (Gap >= 2 means 1+ day off)
        cond_h_before = df_range['Next_Gap_Days'] >= 2
        cond_h_after = df_range['Prev_Gap_Days'] >= 2
        cond_h_other = ~(cond_h_before | cond_h_after)
        
        h_before_mean = df_range[cond_h_before]['Daily_Return'].mean()
        h_after_mean = df_range[cond_h_after]['Daily_Return'].mean()
        h_other_mean = df_range[cond_h_other]['Daily_Return'].mean()
        
        h_before_count = cond_h_before.sum()
        h_after_count = cond_h_after.sum()
        h_other_count = cond_h_other.sum()
        
        h_categories = ['休日前<br>(Before)', '休日後<br>(After)', 'それ以外<br>(Other)']
        h_means = [h_before_mean, h_after_mean, h_other_mean]
        h_counts = [h_before_count, h_after_count, h_other_count]
        
        # Consec Holiday Logic (Gap >= 3 means 2+ days off, usually weekends/long weekends)
        cond_c_before = df_range['Next_Gap_Days'] >= 3
        cond_c_after = df_range['Prev_Gap_Days'] >= 3
        cond_c_other = ~(cond_c_before | cond_c_after)
        
        c_before_mean = df_range[cond_c_before]['Daily_Return'].mean()
        c_after_mean = df_range[cond_c_after]['Daily_Return'].mean()
        c_other_mean = df_range[cond_c_other]['Daily_Return'].mean()
        
        c_before_count = cond_c_before.sum()
        c_after_count = cond_c_after.sum()
        c_other_count = cond_c_other.sum()
        
        c_categories = ['連休前<br>(Before Consec)', '連休後<br>(After Consec)', 'それ以外<br>(Other)']
        c_means = [c_before_mean, c_after_mean, c_other_mean]
        c_counts = [c_before_count, c_after_count, c_other_count]
        
        visible = (i == 0) # Only first period visible by default
        
        h_colors = ['#00CC96' if val >= 0 else '#EF553B' for val in h_means]
        c_colors = ['#00CC96' if val >= 0 else '#EF553B' for val in c_means]
        
        fig.add_trace(go.Bar(
            x=h_categories,
            y=h_means,
            marker_color=h_colors,
            text=[f"{m:+.3f}%" for m in h_means],
            textposition='auto',
            hoverinfo='text',
            hovertemplate="<b>%{x}</b><br>Avg Return: %{y:+.3f}%<br>Days: %{customdata:,}<extra></extra>",
            customdata=h_counts,
            visible=visible,
            name=f"Holiday - {label}"
        ), row=1, col=1)
        
        fig.add_trace(go.Bar(
            x=c_categories,
            y=c_means,
            marker_color=c_colors,
            text=[f"{m:+.3f}%" for m in c_means],
            textposition='auto',
            hoverinfo='text',
            hovertemplate="<b>%{x}</b><br>Avg Return: %{y:+.3f}%<br>Days: %{customdata:,}<extra></extra>",
            customdata=c_counts,
            visible=visible,
            name=f"Consec Holiday - {label}"
        ), row=1, col=2)
        
        # Total traces so far = i*2
        visibility = [False] * (len(ranges) * 2)
        visibility[i*2] = True
        visibility[i*2 + 1] = True
        
        title_text = f"S&P 500 Average Daily Return Around Holidays<br><sup>Data Period: {actual_cutoff} - {end_year} | Measured close-to-close</sup>"
        
        buttons.append(dict(
            label=f"{label} ({actual_cutoff} - {end_year})",
            method="update",
            args=[
                {"visible": visibility},
                {"title": title_text}
            ]
        ))

    fig.update_layout(
        updatemenus=[
            dict(
                type="dropdown",
                direction="down",
                x=0.01,
                xanchor="left",
                y=1.20,
                yanchor="bottom",
                active=0,
                showactive=True,
                buttons=buttons,
                bgcolor="#333",
                font=dict(color="white")
            )
        ],
        title=f"S&P 500 Average Daily Return Around Holidays<br><sup>Data Period: {start_year} - {end_year} | Measured close-to-close</sup>",
        template='plotly_dark',
        showlegend=False
    )
    
    # Update axes titles
    fig.update_yaxes(title_text="Average Daily Return (%)", row=1, col=1)
    
    fig.write_html(output_path)
    print(f"Holiday effect chart successfully saved to {output_path}")

if __name__ == '__main__':
    create_chart()
