import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def create_jp_ytd_anomaly_chart():
    csv_path = 'market_data.csv'
    output_path = 'jp_ytd_anomaly_chart.html'
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
        
    print("Loading Japanese market data for YTD anomaly analysis...")
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

    # Clean data
    df_clean = df.dropna(subset=['Nikkei 225', 'TOPIX'], how='all').copy()
    df_clean['Date'] = df_clean['Date'].dt.tz_localize(None).dt.normalize()
    df_clean = df_clean.drop_duplicates(subset=['Date'], keep='last')
    df_clean = df_clean.sort_values('Date').reset_index(drop=True)
    
    df_clean['Year'] = df_clean['Date'].dt.year
    
    # We want to normalize to Jan-Dec. The best way is to create a complete daily calendar for each year.
    all_years_data = []
    
    for year, group in df_clean.groupby('Year'):
        # create date range for this year
        full_year_dates = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31', freq='D')
        
        # reindex
        group = group.set_index('Date')
        group = group.reindex(full_year_dates)
        
        # forward fill prices
        group['Nikkei 225'] = group['Nikkei 225'].ffill()
        group['TOPIX'] = group['TOPIX'].ffill()
        
        # calculate YTD. The first available value in the year might be after Jan 1 (e.g. Jan 4)
        first_n225 = group['Nikkei 225'].dropna().iloc[0] if not group['Nikkei 225'].dropna().empty else None
        first_topix = group['TOPIX'].dropna().iloc[0] if not group['TOPIX'].dropna().empty else None
        
        if first_n225 is not None:
            group['N225_YTD'] = (group['Nikkei 225'] / first_n225) * 100
        else:
            group['N225_YTD'] = None
            
        if first_topix is not None:
            group['TOPIX_YTD'] = (group['TOPIX'] / first_topix) * 100
        else:
            group['TOPIX_YTD'] = None
            
        group['Year'] = year
        
        # map the date index to an Artificial Date (leap year 2024) to align all years on same X-axis
        group['Artificial_Date'] = group.index.map(lambda d: pd.Timestamp(2024, d.month, d.day))
        
        all_years_data.append(group.reset_index(drop=True))
        
    df_full = pd.concat(all_years_data, ignore_index=True)
    df_full = df_full.dropna(subset=['N225_YTD', 'TOPIX_YTD'], how='all')
    
    start_year = df_full['Year'].min()
    current_year = df_full['Year'].max()
    end_year = current_year
    
    # For the current year, we only want to plot up to the latest available data, not ffilled to Dec 31
    # Actually, df_clean only had data up to today, but reindex filled it to Dec 31 with NaNs, then ffill filled the NaNs!
    # We need to remove the future dates for the current year.
    latest_date_current_year = df_clean[df_clean['Year'] == current_year]['Date'].max()
    if pd.notna(latest_date_current_year):
        artificial_latest = pd.Timestamp(2024, latest_date_current_year.month, latest_date_current_year.day)
        # nullify data after latest date for current year
        df_full.loc[(df_full['Year'] == current_year) & (df_full['Artificial_Date'] > artificial_latest), ['N225_YTD', 'TOPIX_YTD']] = None
        
    df_current_year = df_full[df_full['Year'] == current_year].copy()
    
    ranges = [
        ("All Time", start_year),
        ("Last 30 Years", current_year - 30),
        ("Last 20 Years", current_year - 20),
        ("Last 10 Years", current_year - 10)
    ]

    fig = make_subplots(
        rows=1, cols=2, 
        subplot_titles=("日経平均 年初来推移 (年初=100)", "TOPIX 年初来推移 (年初=100)"),
        horizontal_spacing=0.1
    )
    
    buttons = []
    
    for i, (label, cutoff_year) in enumerate(ranges):
        actual_cutoff = max(cutoff_year, start_year)
        df_range = df_full[df_full['Year'] >= actual_cutoff]
        
        # Calculate daily averages across years
        n225_avg = df_range.groupby('Artificial_Date')['N225_YTD'].mean().reset_index()
        topix_avg = df_range.groupby('Artificial_Date')['TOPIX_YTD'].mean().reset_index()
        
        visible = (i == 0)
        
        # Nikkei 225 Avg
        fig.add_trace(go.Scatter(
            x=n225_avg['Artificial_Date'],
            y=n225_avg['N225_YTD'],
            mode='lines',
            line=dict(color='#00CC96', width=3),
            name=f"Avg ({label})",
            hovertemplate="%{x|%b %d}<br>Avg: %{y:.2f}<extra></extra>",
            visible=visible,
            legendgroup=f"n225_{i}"
        ), row=1, col=1)
        
        # Nikkei 225 Current
        fig.add_trace(go.Scatter(
            x=df_current_year['Artificial_Date'],
            y=df_current_year['N225_YTD'].dropna(),
            mode='lines',
            line=dict(color='#FFD700', width=2, dash='dot'),
            name=f"{current_year}",
            hovertemplate="%{x|%b %d}<br>2026: %{y:.2f}<extra></extra>",
            visible=visible,
            legendgroup=f"n225_{i}"
        ), row=1, col=1)
        
        # TOPIX Avg
        fig.add_trace(go.Scatter(
            x=topix_avg['Artificial_Date'],
            y=topix_avg['TOPIX_YTD'],
            mode='lines',
            line=dict(color='#AB63FA', width=3),
            name=f"Avg ({label})",
            hovertemplate="%{x|%b %d}<br>Avg: %{y:.2f}<extra></extra>",
            visible=visible,
            legendgroup=f"topix_{i}"
        ), row=1, col=2)
        
        # TOPIX Current
        fig.add_trace(go.Scatter(
            x=df_current_year['Artificial_Date'],
            y=df_current_year['TOPIX_YTD'].dropna(),
            mode='lines',
            line=dict(color='#FFD700', width=2, dash='dot'),
            name=f"{current_year}",
            showlegend=False,
            hovertemplate="%{x|%b %d}<br>2026: %{y:.2f}<extra></extra>",
            visible=visible,
            legendgroup=f"topix_{i}"
        ), row=1, col=2)
        
        total_traces = len(ranges) * 4
        visibility = [False] * total_traces
        
        visibility[i*4] = True
        visibility[i*4+1] = True
        visibility[i*4+2] = True
        visibility[i*4+3] = True
        
        title_text = f"日本株 アノマリー 年初来累積推移 (年初=100)<br><sup>Data Period: {actual_cutoff} - {end_year}</sup>"
        
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
        title=f"日本株 アノマリー 年初来累積推移 (年初=100)<br><sup>Data Period: {start_year} - {end_year}</sup>",
        template='plotly_dark',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified" # x unified works really well with dates
    )
    
    # Format x axes to show months
    fig.update_xaxes(
        title_text="月 (Month)", 
        tickformat="%b", # formats as Jan, Feb, Mar...
        dtick="M1", # tick every 1 month
        row=1, col=1
    )
    fig.update_xaxes(
        title_text="月 (Month)", 
        tickformat="%b",
        dtick="M1",
        row=1, col=2
    )
    fig.update_yaxes(title_text="Index (年初=100)", row=1, col=1)
    
    # Add horizontal line at 100 for reference
    fig.add_hline(y=100, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.write_html(output_path)
    print(f"YTD Anomaly chart successfully saved to {output_path}")

if __name__ == '__main__':
    create_jp_ytd_anomaly_chart()
