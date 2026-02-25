import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def create_jp_anomaly_chart():
    csv_path = 'market_data.csv'
    output_path = 'jp_anomaly_chart.html'
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
        
    print("Loading Japanese market data for anomaly analysis...")
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
    
    # Calculate Monthly Returns
    # Set date as index, resample by month-end to get the last trading day of each month
    df_monthly = df_clean.set_index('Date').resample('ME').last()
    
    df_monthly['N225_Monthly_Return'] = df_monthly['Nikkei 225'].pct_change() * 100
    df_monthly['TOPIX_Monthly_Return'] = df_monthly['TOPIX'].pct_change() * 100
    
    # Forward fill is not strictly necessary for monthly returns if we drop na, but to be sure we just drop.
    df_monthly = df_monthly.dropna(subset=['N225_Monthly_Return', 'TOPIX_Monthly_Return'], how='all').copy()
    
    df_monthly['Month'] = df_monthly.index.month
    df_monthly['Year'] = df_monthly.index.year
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_order = list(range(1, 13))
    
    start_year = df_monthly['Year'].min()
    end_year = df_monthly['Year'].max()
    current_year = 2026 # df_monthly['Year'].max() is likely 2026
    
    # Fetch this year's data specifically for comparison line
    df_current_year = df_monthly[df_monthly['Year'] == current_year]
    
    n225_current_returns = [None]*12
    topix_current_returns = [None]*12
    for _, row in df_current_year.iterrows():
        m_idx = int(row['Month']) - 1
        n225_current_returns[m_idx] = row['N225_Monthly_Return']
        topix_current_returns[m_idx] = row['TOPIX_Monthly_Return']

    ranges = [
        ("All Time", start_year),
        ("Last 30 Years", current_year - 30),
        ("Last 20 Years", current_year - 20),
        ("Last 10 Years", current_year - 10)
    ]

    fig = make_subplots(
        rows=1, cols=2, 
        subplot_titles=("日経平均 月間リターン", "TOPIX 月間リターン"),
        horizontal_spacing=0.1
    )
    
    buttons = []
    
    # We will add 3 traces per subplot per range:
    # 1. Bar chart (Average Return) - though user asked for "line chart", usually anomaly is bar, but let's change average to Line Chart as well to make it a pure Line Chart.
    
    # Note: User request: "折れ線グラフにして、今年の線を比較で出して" -> Average should be line, Current year should be another line.
    
    for i, (label, cutoff_year) in enumerate(ranges):
        actual_cutoff = max(cutoff_year, start_year)
        df_range = df_monthly[df_monthly['Year'] >= actual_cutoff]
        
        # Nikkei 225 stats
        n225_stats = df_range.groupby('Month').agg(
            Avg_Return=('N225_Monthly_Return', 'mean'),
            Hit_Rate=('N225_Monthly_Return', lambda x: (x > 0).mean() * 100),
            Count=('N225_Monthly_Return', 'count')
        ).reindex(month_order)
        
        # TOPIX stats
        topix_stats = df_range.groupby('Month').agg(
            Avg_Return=('TOPIX_Monthly_Return', 'mean'),
            Hit_Rate=('TOPIX_Monthly_Return', lambda x: (x > 0).mean() * 100),
            Count=('TOPIX_Monthly_Return', 'count')
        ).reindex(month_order)
        
        visible = (i == 0) # Only first period visible by default
        
        # Nikkei 225 Traces (Row 1, Col 1)
        # 1. Historical Average Line
        fig.add_trace(go.Scatter(
            x=month_names,
            y=n225_stats['Avg_Return'],
            mode='lines+markers',
            line=dict(color='#00CC96', width=3),
            marker=dict(size=8),
            name=f"Avg ({label})",
            hovertemplate="<b>%{x}</b><br>Historical Avg: %{y:+.2f}%<br>Win Rate: %{customdata[0]:.1f}%<br>Count: %{customdata[1]}<extra></extra>",
            customdata=n225_stats[['Hit_Rate', 'Count']].values,
            visible=visible,
            legendgroup=f"n225_{i}"
        ), row=1, col=1)
        
        # 2. Current Year Line
        fig.add_trace(go.Scatter(
            x=month_names,
            y=n225_current_returns,
            mode='lines+markers',
            line=dict(color='#FFD700', width=3, dash='dot'),
            marker=dict(size=8, symbol='star'),
            name=f"{current_year}",
            hovertemplate="<b>%{x}</b><br>2026 Return: %{y:+.2f}%<extra></extra>",
            visible=visible,
            legendgroup=f"n225_{i}"
        ), row=1, col=1)

        # TOPIX Traces (Row 1, Col 2)
        # 3. Historical Average Line
        fig.add_trace(go.Scatter(
            x=month_names,
            y=topix_stats['Avg_Return'],
            mode='lines+markers',
            line=dict(color='#AB63FA', width=3),
            marker=dict(size=8),
            name=f"Avg ({label})",
            hovertemplate="<b>%{x}</b><br>Historical Avg: %{y:+.2f}%<br>Win Rate: %{customdata[0]:.1f}%<br>Count: %{customdata[1]}<extra></extra>",
            customdata=topix_stats[['Hit_Rate', 'Count']].values,
            visible=visible,
            legendgroup=f"topix_{i}"
        ), row=1, col=2)
        
        # 4. Current Year Line
        fig.add_trace(go.Scatter(
            x=month_names,
            y=topix_current_returns,
            mode='lines+markers',
            line=dict(color='#FFD700', width=3, dash='dot'),
            marker=dict(size=8, symbol='star'),
            name=f"{current_year}",
            showlegend=False, # Shared legend look
            hovertemplate="<b>%{x}</b><br>2026 Return: %{y:+.2f}%<extra></extra>",
            visible=visible,
            legendgroup=f"topix_{i}"
        ), row=1, col=2)
        
        # Visibility logic: 4 traces per range
        total_traces = len(ranges) * 4
        visibility = [False] * total_traces
        
        visibility[i*4] = True
        visibility[i*4+1] = True
        visibility[i*4+2] = True
        visibility[i*4+3] = True
        
        title_text = f"日本株 月別アノマリー (平均リターン vs {current_year}年)<br><sup>Data Period: {actual_cutoff} - {end_year}</sup>"
        
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
        title=f"日本株 月別アノマリー (平均リターン vs {current_year}年)<br><sup>Data Period: {start_year} - {end_year}</sup>",
        template='plotly_dark',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified"
    )
    
    # Add a zero line to Y axes
    fig.update_yaxes(zeroline=True, zerolinewidth=1, zerolinecolor='gray')
    fig.update_yaxes(title_text="Monthly Return (%)", row=1, col=1)
    
    fig.write_html(output_path)
    print(f"Anomaly chart (line style) successfully saved to {output_path}")

if __name__ == '__main__':
    create_jp_anomaly_chart()
