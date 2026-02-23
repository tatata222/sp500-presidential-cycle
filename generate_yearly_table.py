import pandas as pd
import plotly.graph_objects as go
import os

def create_table():
    csv_path = 'market_data.csv'
    output_path = 'yearly_table.html'
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
        
    print("Loading data for table...")
    try:
        df = pd.read_csv(csv_path)
        df['Date'] = pd.to_datetime(df['Date'], utc=True)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    print("Processing data...")
    df['Year'] = df['Date'].dt.year
    target_col = 'S&P 500'
    
    if target_col not in df.columns:
        print(f"Column {target_col} not found in the CSV.")
        return

    # Drop rows with NaN in target column
    df_clean = df.dropna(subset=[target_col])
    
    years = sorted(df_clean['Year'].unique())
    table_data = []

    def get_cycle_labels(year):
        if year % 4 == 1:
            return "Year 1: Post-Election"
        elif year % 4 == 2:
            return "Year 2: Midterm"
        elif year % 4 == 3:
            return "Year 3: Pre-Election"
        else:
            return "Year 4: Election"

    for year in years:
        subset = df_clean[df_clean['Year'] == year].sort_values('Date')
        if subset.empty:
            continue
            
        start_price = subset.iloc[0][target_col]
        end_price = subset.iloc[-1][target_col]
        
        # Calculate return percentage
        return_pct = ((end_price - start_price) / start_price) * 100
        
        table_data.append({
            'Year': year,
            'Cycle': get_cycle_labels(year),
            'Start Price': round(start_price, 2),
            'End Price': round(end_price, 2),
            'Return (%)': round(return_pct, 2)
        })

    # Convert to DataFrame for easy processing
    table_df = pd.DataFrame(table_data)
    
    # Sort descending by year to show recent years first
    table_df = table_df.sort_values('Year', ascending=False)
    
    # Define colors based on return (Green for positive, Red for negative)
    colors = ['#1a1a1a'] * len(table_df) # Default header/background
    
    # Cell colors
    cell_colors = [
        ['#2a2a2a'] * len(table_df), # Year column
        ['#2a2a2a'] * len(table_df), # Cycle column
        ['#2a2a2a'] * len(table_df), # Start price
        ['#2a2a2a'] * len(table_df), # End price
        ['#00441b' if val >= 0 else '#67000d' for val in table_df['Return (%)']] # Return col: dark green/dark red
    ]
    
    # Font colors for better contrast
    font_colors = [
        ['white'] * len(table_df),
        ['white'] * len(table_df),
        ['white'] * len(table_df),
        ['white'] * len(table_df),
        ['#00ff00' if val >= 0 else '#ff4444' for val in table_df['Return (%)']] # Bright green/red
    ]

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(table_df.columns),
            fill_color='#111111',
            align='center',
            font=dict(color='white', size=14),
            height=40
        ),
        cells=dict(
            values=[table_df.Year, table_df.Cycle, table_df['Start Price'], table_df['End Price'], table_df['Return (%)']],
            fill_color=cell_colors,
            align=['center', 'center', 'right', 'right', 'right'],
            font=dict(color=font_colors, size=13),
            height=30,
            format=["d", "", ".2f", ".2f", "+.2f"] # Format rules
        )
    )])
    
    # Calculate some summary stats to add to title
    avg_return = table_df['Return (%)'].mean()
    win_rate = (table_df['Return (%)'] > 0).mean() * 100
    
    fig.update_layout(
        title=f"S&P 500 Yearly Returns (Average: {avg_return:.2f}% | Positive Years: {win_rate:.1f}%)",
        template='plotly_dark',
        margin=dict(l=20, r=20, t=60, b=20)
    )

    fig.write_html(output_path)
    print(f"Table successfully saved to {output_path}")

if __name__ == '__main__':
    create_table()
