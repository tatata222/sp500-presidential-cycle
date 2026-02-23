import pandas as pd
import plotly.graph_objects as go
import os

def create_weekday_table():
    csv_path = 'market_data.csv'
    output_path = 'weekday_table.html'
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
        
    print("Loading data for weekday table...")
    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'], utc=True)
    
    target_col = 'S&P 500'
    df_clean = df.dropna(subset=[target_col]).copy()
    
    # 完全にカレンダー通りの「1日単位」のデータを作成して前日比を計算
    df_clean['Date'] = df_clean['Date'].dt.tz_localize(None).dt.normalize()
    df_clean = df_clean.drop_duplicates(subset=['Date'], keep='last')
    df_clean = df_clean.set_index('Date').resample('D').ffill()
    
    df_clean['Daily_Return'] = df_clean[target_col].pct_change() * 100
    df_clean['Weekday_Num'] = df_clean.index.dayofweek
    df_clean['Weekday'] = df_clean.index.day_name()
    
    # 計算し終わったらNaNを除外
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
    
    for i, (label, cutoff_year) in enumerate(ranges):
        actual_cutoff = max(cutoff_year, start_year)
        
        df_range = df_clean[df_clean['Year'] >= actual_cutoff]
        # 土日は除外（取引がないため常に0%となって平均を崩すので）
        df_range_tradable = df_range[~df_range['Weekday_Num'].isin([5, 6])]
        
        weekday_stats = df_range_tradable.groupby(['Weekday_Num', 'Weekday']).agg(
            Avg_Return=('Daily_Return', 'mean'),
            Hit_Rate=('Daily_Return', lambda x: (x > 0).mean() * 100),
            Count=('Daily_Return', 'count')
        ).reset_index()
        
        weekday_stats = weekday_stats.sort_values('Weekday_Num')

        cell_colors = [
            ['#2a2a2a'] * len(weekday_stats),
            ['#00441b' if val >= 0 else '#67000d' for val in weekday_stats['Avg_Return']],
            ['#2a2a2a'] * len(weekday_stats),
            ['#2a2a2a'] * len(weekday_stats)
        ]
        
        font_colors = [
            ['white'] * len(weekday_stats),
            ['#00ff00' if val >= 0 else '#ff4444' for val in weekday_stats['Avg_Return']],
            ['white'] * len(weekday_stats),
            ['white'] * len(weekday_stats)
        ]
        
        visible = (i == 0)
        
        table_trace = go.Table(
            visible=visible,
            name=label,
            header=dict(
                values=['Day of the Week', 'Avg Return (%)', 'Hit Rate (%)', 'Total Trading Days'],
                fill_color='#111111',
                align='center',
                font=dict(color='white', size=14),
                height=40
            ),
            cells=dict(
                values=[
                    weekday_stats['Weekday'], 
                    weekday_stats['Avg_Return'], 
                    weekday_stats['Hit_Rate'], 
                    weekday_stats['Count']
                ],
                fill_color=cell_colors,
                font=dict(color=font_colors, size=13),
                align=['center', 'right', 'right', 'right'],
                height=30,
                format=["", "+.3f", ".1f", "d"]
            )
        )
        fig.add_trace(table_trace)

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
                {"title": f"S&P 500 Weekday Data Table<br><sup>Data Period: {actual_cutoff} - {end_year} | Measured close-to-close</sup>"}
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
        title=f"S&P 500 Weekday Data Table<br><sup>Data Period: {start_year} - {end_year} | Measured close-to-close</sup>",
        template='plotly_dark',
        margin=dict(l=20, r=20, t=80, b=20)
    )

    fig.write_html(output_path)
    print(f"Table successfully saved to {output_path}")

if __name__ == '__main__':
    create_weekday_table()
