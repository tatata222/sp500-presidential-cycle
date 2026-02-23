import pandas as pd
import os
from datetime import datetime, timezone

def create_index():
    csv_path = 'market_data.csv'
    output_path = 'index.html'
    
    latest_date_str = "Unknown"
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            # Find the maximum date
            df['Date'] = pd.to_datetime(df['Date'], utc=True)
            latest_date_str = df['Date'].max().strftime('%Y-%m-%d')
        except Exception as e:
            print(f"Error reading {csv_path}: {e}")
            
    # current UTC time as generation time
    gen_time_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    html_content = f"""<!DOCTYPE html>
<html lang="ja">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>S&P 500 Presidential Cycle Analysis</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #ffffff;
            margin: 0;
            padding: 0;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}

        h1 {{
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 10px;
            color: #e0e0e0;
        }}

        p.subtitle {{
            text-align: center;
            color: #a0a0a0;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }}
        
        .update-info {{
            text-align: center;
            color: #707070;
            font-size: 0.9rem;
            margin-bottom: 50px;
        }}
        .update-info span {{
            color: #00CC96;
            font-weight: 600;
        }}

        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 30px;
        }}

        .card {{
            background-color: #1e1e1e;
            border-radius: 12px;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            border: 1px solid #333;
        }}

        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5);
            border-color: #555;
        }}

        .iframe-container {{
            position: relative;
            width: 100%;
            height: 250px;
            overflow: hidden;
            background-color: #000;
        }}

        .iframe-container iframe {{
            position: absolute;
            top: 0;
            left: 0;
            width: 150%;
            height: 150%;
            transform: scale(0.666);
            transform-origin: 0 0;
            border: none;
            pointer-events: none;
            /* iframe内をクリックさせない */
        }}

        .iframe-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 10;
        }}

        .card-content {{
            padding: 20px;
            flex-grow: 1;
        }}

        .card-title {{
            font-size: 1.25rem;
            font-weight: 600;
            margin: 0 0 10px 0;
            color: #f0f0f0;
        }}

        .card-desc {{
            font-size: 0.95rem;
            color: #b0b0b0;
            margin: 0;
            line-height: 1.5;
        }}

        @media (max-width: 768px) {{
            .gallery {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>

<body>

    <div class="container">
        <h1>S&P 500 Presidential Cycle Analysis</h1>
        <p class="subtitle">大統領選挙サイクルに基づく S&P 500 の過去データ分析ダッシュボード</p>
        <div class="update-info">
            Data valid as of: <span>{latest_date_str}</span>&nbsp; | &nbsp;Last Generated: {gen_time_str}
        </div>

        <div class="gallery">

            <a href="yearly_chart.html" class="card">
                <div class="iframe-container">
                    <iframe src="yearly_chart.html" scrolling="no" tabindex="-1"></iframe>
                    <div class="iframe-overlay"></div>
                </div>
                <div class="card-content">
                    <h2 class="card-title">Yearly Chart by Election Cycle</h2>
                    <p class="card-desc">大統領選挙の4年サイクル（選挙後、中間選挙、大統領選前、大統領選）ごとの年間平均パフォーマンスを比較します。</p>
                </div>
            </a>

            <a href="weekday_chart.html" class="card">
                <div class="iframe-container">
                    <iframe src="weekday_chart.html" scrolling="no" tabindex="-1"></iframe>
                    <div class="iframe-overlay"></div>
                </div>
                <div class="card-content">
                    <h2 class="card-title">Weekday Average Returns</h2>
                    <p class="card-desc">月曜日から金曜日まで、曜日ごとの平均的なリターンや過去の勝率について分析したチャートです。</p>
                </div>
            </a>

            <a href="daily_return_distribution_chart.html" class="card">
                <div class="iframe-container">
                    <iframe src="daily_return_distribution_chart.html" scrolling="no" tabindex="-1"></iframe>
                    <div class="iframe-overlay"></div>
                </div>
                <div class="card-content">
                    <h2 class="card-title">Daily Return Distribution</h2>
                    <p class="card-desc">過去のデータから1日の「騰落率（＋／－）」の分布を可視化。相場の変動幅（ボラティリティ）を直感的に把握できます。</p>
                </div>
            </a>

            <a href="absolute_return_distribution_chart.html" class="card">
                <div class="iframe-container">
                    <iframe src="absolute_return_distribution_chart.html" scrolling="no" tabindex="-1"></iframe>
                    <div class="iframe-overlay"></div>
                </div>
                <div class="card-content">
                    <h2 class="card-title">Absolute Return Ranges</h2>
                    <p class="card-desc">絶対値での変動幅ごとに、プラスリターンとマイナスリターンがそれぞれどのくらいの割合で発生しているかを比較します。</p>
                </div>
            </a>

            <a href="yield_history_chart.html" class="card">
                <div class="iframe-container">
                    <iframe src="yield_history_chart.html" scrolling="no" tabindex="-1"></iframe>
                    <div class="iframe-overlay"></div>
                </div>
                <div class="card-content">
                    <h2 class="card-title">US 10-Year Treasury Yield History</h2>
                    <p class="card-desc">過去から現在までの米10年債利回りとS&P 500の長期的な推移を示す折れ線グラフです。</p>
                </div>
            </a>

            <a href="daily_2025_table.html" class="card">
                <div class="iframe-container" style="background-color: #111;">
                    <iframe src="daily_2025_table.html" scrolling="no" tabindex="-1"></iframe>
                    <div class="iframe-overlay"></div>
                </div>
                <div class="card-content">
                    <h2 class="card-title">Daily Returns Table (2025)</h2>
                    <p class="card-desc">2025年の日々のS&P 500の終値データと騰落率をまとめたデータテーブルです。</p>
                </div>
            </a>

        </div>
    </div>

</body>

</html>
"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Successfully generated {output_path} (Data Date: {latest_date_str})")

if __name__ == '__main__':
    create_index()
