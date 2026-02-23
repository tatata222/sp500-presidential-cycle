import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

def fetch_and_plot_market_data():
    # Define tickers
    tickers = {
        '^GSPC': 'S&P 500',
        '^NDX': 'NASDAQ 100',
        '^TNX': 'US 10-Year Treasury Yield'
    }

    # Fetch data
    print("Fetching data...")
    data = {}
    # Combine data into a single DataFrame
    market_df = pd.DataFrame()
    for ticker, name in tickers.items():
        try:
            # Fetch max history
            df = yf.Ticker(ticker).history(period="max")
            if not df.empty:
                # Rename the Series to the name
                series = df['Close'].rename(name)
                # Join to the main DataFrame
                if market_df.empty:
                    market_df = pd.DataFrame(series)
                else:
                    market_df = market_df.join(series, how='outer')
                
                # Also keep in data dict for plotting
                data[name] = series
                print(f"Data fetched for {name}: {len(df)} records")
            else:
                print(f"No data found for {name}")
        except Exception as e:
            print(f"Error fetching {name}: {e}")

    # Save to CSV
    if not market_df.empty:
        csv_file = 'market_data.csv'
        market_df.to_csv(csv_file)
        print(f"Data saved to {csv_file}")

    if not data:
        print("No data available to plot.")
        return

    # Create figure and axis
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Plot Stock Indices on Left Y-Axis
    color = 'tab:blue'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Index Value (S&P 500, NASDAQ 100)', color=color)
    
    if 'S&P 500' in data:
        ax1.plot(data['S&P 500'].index, data['S&P 500'], label='S&P 500', color='blue', linewidth=1.5)
    if 'NASDAQ 100' in data:
        ax1.plot(data['NASDAQ 100'].index, data['NASDAQ 100'], label='NASDAQ 100', color='cyan', linewidth=1.5)
    
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Instantiate a second axes that shares the same x-axis
    ax2 = ax1.twinx()  
    color = 'tab:red'
    ax2.set_ylabel('Interest Rate % (10-Year Treasury Yield)', color=color)  
    
    if 'US 10-Year Treasury Yield' in data:
        ax2.plot(data['US 10-Year Treasury Yield'].index, data['US 10-Year Treasury Yield'], label='10-Year Treasury Yield', color='red', linewidth=1.5, alpha=0.7)
    
    ax2.tick_params(axis='y', labelcolor=color)

    # Title and Layout
    plt.title('US Market Data: S&P 500, NASDAQ 100, and 10-Year Treasury Yield')
    fig.tight_layout()  # otherwise the right y-label is slightly clipped

    # Add legends
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left')

    # Save plot
    output_file = 'market_data_chart.png'
    plt.savefig(output_file)
    print(f"Chart saved as {output_file}")

if __name__ == "__main__":
    fetch_and_plot_market_data()
