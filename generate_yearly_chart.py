import pandas as pd
import plotly.graph_objects as go
import os

def create_chart():
    csv_path = 'market_data.csv'
    output_path = 'yearly_chart.html'
    
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

    # First, drop rows that have no price for the target column
    df_clean = df.dropna(subset=[target_col]).copy()
    
    # Forward-fill missing days (weekends, holidays) with previous close price
    df_clean['Date'] = df_clean['Date'].dt.tz_localize(None).dt.normalize()
    df_clean = df_clean.drop_duplicates(subset=['Date'], keep='last')
    df_clean = df_clean.set_index('Date').resample('D').ffill().reset_index()
    
    df_clean['Year'] = df_clean['Date'].dt.year
    df_clean['MonthDay'] = df_clean['Date'].dt.strftime('%m-%d')
    # Use 2000 (leap year) to parse MonthDay to datetime
    df_clean['PlotDate'] = pd.to_datetime('2000-' + df_clean['MonthDay'], format='%Y-%m-%d', errors='coerce')
    
    # Drop any rows where PlotDate failed to parse
    df_clean = df_clean.dropna(subset=['PlotDate'])

    years = sorted(df_clean['Year'].unique())
    all_normalized_data = []
    
    for year in years:
        subset = df_clean[df_clean['Year'] == year].sort_values('PlotDate').copy()
        if subset.empty:
            continue
            
        start_price = subset.iloc[0][target_col]
        # start_price should not be 0; but if it is, this avoids division by zero warning
        if start_price == 0:
            continue
            
        subset['Normalized_Price'] = (subset[target_col] / start_price) * 100
        all_normalized_data.append(subset)
        
    if not all_normalized_data:
        print("No data available.")
        return
        
    df_norm = pd.concat(all_normalized_data)
    
    def get_cycle_labels(year):
        if year % 4 == 1:
            return "Year 1: Post-Election"
        elif year % 4 == 2:
            return "Year 2: Midterm"
        elif year % 4 == 3:
            return "Year 3: Pre-Election"
        else:
            return "Year 4: Election"
            
    df_norm['Cycle'] = df_norm['Year'].apply(get_cycle_labels)

    current_year = 2026
    current_cycle = get_cycle_labels(current_year)
    
    ranges = [
        ("All Time", years[0]),
        ("Last 50 Years", current_year - 50),
        ("Last 30 Years", current_year - 30),
        ("Last 20 Years", current_year - 20),
        ("Last 10 Years", current_year - 10)
    ]
    
    cycles = [
        "Year 1: Post-Election",
        "Year 2: Midterm",
        "Year 3: Pre-Election",
        "Year 4: Election"
    ]
    
    colors = {
        "Year 1: Post-Election": "#636EFA",
        "Year 2: Midterm": "#EF553B",
        "Year 3: Pre-Election": "#00CC96",
        "Year 4: Election": "#AB63FA"
    }

    fig = go.Figure()
    
    # 366 dates for the leap year mapping
    all_monthdays = pd.date_range("2000-01-01", "2000-12-31").strftime('%m-%d')
    all_plotdates = pd.date_range("2000-01-01", "2000-12-31")
    
    month_ends_monthday = pd.date_range("2000-01-01", "2000-12-31", freq='ME').strftime('%m-%d').tolist()

    # Arrays to store values for the "Smoothing" updatemenu
    y_raw_list = []
    y_sma_list = []
    ht_raw_list = []
    ht_sma_list = []
    
    scatter_indices_to_update = []
    box_indices_to_update = []
    box_ht_list = []
    box_y_on_list = []
    box_y_off_list = []
    
    current_trace_index = 0

    print("Generating traces...")
    
    for i, (label, start_yr) in enumerate(ranges):
        actual_start_yr = max(start_yr, years[0])
        df_range = df_norm[df_norm['Year'] >= actual_start_yr]
        
        visible = (i == 1) # Default to 'Last 50 Years'
        
        # 1. Add BOX TRACES for each cycle (drawn behind the lines)
        for cycle in cycles:
            subset = df_range[df_range['Cycle'] == cycle]
            box_data = subset[subset['MonthDay'].isin(month_ends_monthday)]
            
            ht_box = f"Cycle: {cycle}<br>Month End: %{{x|%b}}<br>Distribution: %{{y:.2f}}<extra></extra>"
            box_ht_list.append(ht_box)
            box_indices_to_update.append(current_trace_index)
            
            box_y_on_list.append(box_data['Normalized_Price'].values)
            box_y_off_list.append([None] * len(box_data))
            
            fig.add_trace(go.Box(
                x=box_data['PlotDate'],
                y=[None] * len(box_data), # Default to Box off
                name=f"{cycle}",
                visible=visible,
                marker_color=colors[cycle],
                boxpoints=False, # 'outliers' makes the chart too messy, False only shows the Box
                showlegend=False,
                legendgroup=cycle,
                hovertemplate=ht_box
            ))
            current_trace_index += 1
        
        # 2. Add LINE TRACES for each cycle
        for cycle in cycles:
            subset = df_range[df_range['Cycle'] == cycle]
            
            # Pivot to align exactly on calendar dates (MonthDay)
            pivot_df = subset.pivot(index='MonthDay', columns='Year', values='Normalized_Price')
            pivot_df = pivot_df.reindex(all_monthdays)
            
            daily_avg = pivot_df.mean(axis=1)
            sma_30 = daily_avg.rolling(window=30, min_periods=1).mean()
            
            y_raw_list.append(daily_avg.values)
            y_sma_list.append(sma_30.values)
            
            ht_raw = f"Cycle: {cycle}<br>Date: %{{x|%m-%d}}<br>Daily Avg: %{{y:.2f}}<extra></extra>"
            ht_sma = f"Cycle: {cycle}<br>Date: %{{x|%m-%d}}<br>30-Day SMA: %{{y:.2f}}<extra></extra>"
            
            ht_raw_list.append(ht_raw)
            ht_sma_list.append(ht_sma)
            
            scatter_indices_to_update.append(current_trace_index)
            
            fig.add_trace(go.Scatter(
                x=all_plotdates,
                y=daily_avg.values, # default is Raw
                mode='lines',
                name=cycle,
                visible=visible,
                opacity=0.9,
                connectgaps=True,
                line=dict(width=3, color=colors[cycle]),
                legendgroup=cycle,
                hovertemplate=ht_raw # default is Raw
            ))
            current_trace_index += 1
            
        # 3. Add Current Year Trace
        curr_y_raw = pd.Series([None]*366, index=all_monthdays)
        curr_y_sma = pd.Series([None]*366, index=all_monthdays)
        
        if current_year in df_norm['Year'].values:
            current_year_data = df_norm[df_norm['Year'] == current_year]
            current_year_data = current_year_data.drop_duplicates(subset=['MonthDay'], keep='last')
            
            curr_series = current_year_data.set_index('MonthDay')['Normalized_Price']
            curr_series = curr_series.reindex(all_monthdays)
            
            curr_y_raw = curr_series
            curr_y_sma = curr_series.rolling(window=30, min_periods=1).mean()
            
        y_raw_list.append(curr_y_raw.values)
        y_sma_list.append(curr_y_sma.values)
        
        ht_c_raw = f"Year: {current_year}<br>Date: %{{x|%m-%d}}<br>Price: %{{y:.2f}}<extra></extra>"
        ht_c_sma = f"Year: {current_year}<br>Date: %{{x|%m-%d}}<br>30-Day SMA: %{{y:.2f}}<extra></extra>"
        
        ht_raw_list.append(ht_c_raw)
        ht_sma_list.append(ht_c_sma)
        
        scatter_indices_to_update.append(current_trace_index)
        
        fig.add_trace(go.Scatter(
            x=all_plotdates,
            y=curr_y_raw.values, # default is Raw
            mode='lines',
            name=f"Current Year: {current_year} ({current_cycle})",
            visible=visible,
            opacity=1.0,
            connectgaps=True,
            line=dict(width=4, color='white', dash='solid'),
            hovertemplate=ht_c_raw # default is Raw
        ))
        current_trace_index += 1

    # Configure drop-down menu buttons for "Period"
    period_buttons = []
    traces_per_group = 4 + 4 + 1 # 4 boxes, 4 lines, 1 curr year
    
    for i, (label, start_yr) in enumerate(ranges):
        actual_start_yr = max(start_yr, years[0])
        visibility = [False] * (len(ranges) * traces_per_group)
        visibility[i*traces_per_group : (i+1)*traces_per_group] = [True] * traces_per_group
            
        period_buttons.append(dict(
            label=f"{label} ({actual_start_yr} - {years[-1]})",
            method="update",
            args=[
                {"visible": visibility},
                {"title": f"S&P 500 Presidential Cycle Average vs {current_year}<br><sup>Data Period: {actual_start_yr} - {years[-1]}</sup>"}
            ]
        ))

    # Configure drop-down menu buttons for "Smoothing Mode"
    smoothing_buttons = [
        dict(
            label="30-Day Moving Average",
            method="restyle",
            args=[
                {"y": y_sma_list, "hovertemplate": ht_sma_list},
                scatter_indices_to_update # specifically only target the Line Traces
            ]
        ),
        dict(
            label="Daily Value (Raw)",
            method="restyle",
            args=[
                {"y": y_raw_list, "hovertemplate": ht_raw_list},
                scatter_indices_to_update # specifically only target the Line Traces
            ]
        )
    ]

    # Configure drop-down menu buttons for "Boxplots"
    boxplot_buttons = [
        dict(
            label="Box Plots: Off",
            method="restyle",
            args=[
                {"y": box_y_off_list, "hoverinfo": "skip"},
                box_indices_to_update
            ]
        ),
        dict(
            label="Box Plots: On",
            method="restyle",
            args=[
                {"y": box_y_on_list, "hoverinfo": "all"},
                box_indices_to_update
            ]
        )
    ]

    fig.update_layout(
        updatemenus=[
            dict(
                type="dropdown",
                direction="down",
                x=0.01,
                xanchor="left",
                y=1.12,
                yanchor="bottom",
                active=1, # Default is Period 1 (Last 50 Years)
                showactive=True,
                buttons=period_buttons,
                bgcolor="#333",
                font=dict(color="white")
            ),
            dict(
                type="dropdown",
                direction="down",
                x=0.30,
                xanchor="left",
                y=1.12,
                yanchor="bottom",
                active=1, # default is Daily Value (Raw)
                showactive=True,
                buttons=smoothing_buttons,
                bgcolor="#333",
                font=dict(color="white")
            ),
            dict(
                type="dropdown",
                direction="down",
                x=0.53,
                xanchor="left",
                y=1.12,
                yanchor="bottom",
                active=0, # default is Box Plots On
                showactive=True,
                buttons=boxplot_buttons,
                bgcolor="#333",
                font=dict(color="white")
            )
        ],
        title=f'S&P 500 Presidential Cycle Average vs Current Year ({current_year})<br><sup>Data Period: {max(ranges[1][1], years[0])} - {years[-1]}</sup>',
        xaxis_title='Date',
        yaxis_title='Normalized Price (Start of Year = 100)',
        xaxis_tickformat='%m-%d',
        hovermode='x unified',
        boxmode='group', # Groups the boxplots together at each month-end tick without overlapping
        template='plotly_dark'
    )
    
    fig.write_html(output_path)
    print(f"Chart successfully saved to {output_path}")

if __name__ == '__main__':
    create_chart()
