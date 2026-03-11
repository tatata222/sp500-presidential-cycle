import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

elections_data = [
    # Date, Type, RulingWon
    ('2024-10-27', '衆院選', False),
    ('2021-10-31', '衆院選', True),
    ('2017-10-22', '衆院選', True),
    ('2014-12-14', '衆院選', True),
    ('2012-12-16', '衆院選', False), # 野党自民が大勝、当時の与党民主は敗北
    ('2009-08-30', '衆院選', False), # 与党自民が敗北、民主党へ政権交代
    ('2005-09-11', '衆院選', True),
    ('2003-11-09', '衆院選', True),
    ('2000-06-25', '衆院選', True),
    ('1996-10-20', '衆院選', True),
    ('1993-07-18', '衆院選', False), # 与党自民が過半数割れ、非自民連立へ
    ('1990-02-18', '衆院選', True),
    ('1986-07-06', '衆院選', True),
    ('1983-12-18', '衆院選', False), # 自民党が過半数割れ（のちに追加公認で過半数）実質敗退扱い
    ('1980-06-22', '衆院選', True),
    
    ('2022-07-10', '参院選', True),
    ('2019-07-21', '参院選', True),
    ('2016-07-10', '参院選', True),
    ('2013-07-21', '参院選', True),
    ('2010-07-11', '参院選', False), # 与党民主党が過半数割れ
    ('2007-07-29', '参院選', False), # 与党自民党が大敗
    ('2004-07-11', '参院選', True), # 自民推移
    ('2001-07-29', '参院選', True),
    ('1998-07-12', '参院選', False), # 与党自民敗退、橋本首相退陣
    ('1995-07-23', '参院選', False), # 与党（社会党など）敗退
    ('1992-07-26', '参院選', True),
    ('1989-07-23', '参院選', False), # 自民大敗（マドンナ旋風）
    ('1986-07-06', '参院選', True), # 衆参同日選
    ('1983-06-26', '参院選', True),
]

def create_election_anomaly_chart():
    csv_path = 'market_data.csv'
    output_path = 'jp_election_anomaly_chart.html'
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
        
    print("Loading Japanese market data for Election anomaly analysis...")
    try:
        df = pd.read_csv(csv_path)
        df['Date'] = pd.to_datetime(df['Date'], utc=True).dt.tz_localize(None).dt.normalize()
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Check if necessary columns exist
    if 'Nikkei 225' not in df.columns:
        print("Nikkei 225 column not found.")
        return

    df_clean = df.dropna(subset=['Nikkei 225']).copy()
    df_clean = df_clean.sort_values('Date').reset_index(drop=True)
    df_clean = df_clean[['Date', 'Nikkei 225']]
    
    # helper: find the nearest trading day
    def get_nearest_trading_day(target_date, direction='backward'):
        if direction == 'backward':
            past_dates = df_clean[df_clean['Date'] <= target_date]
            if not past_dates.empty:
                return past_dates.iloc[-1]['Date'], past_dates.iloc[-1]['Nikkei 225']
        elif direction == 'forward':
            future_dates = df_clean[df_clean['Date'] >= target_date]
            if not future_dates.empty:
                return future_dates.iloc[0]['Date'], future_dates.iloc[0]['Nikkei 225']
        return None, None

    results = []

    for edate_str, etype, ewin in elections_data:
        edate = pd.to_datetime(edate_str)
        # Election date is usually Sunday. Get the price on the Friday before and Monday after
        e_last_trade_date, e_price = get_nearest_trading_day(edate, 'backward')
        
        if e_price is None:
            continue
            
        # 1 month before (approx 30 days)
        mb1_date = edate - pd.Timedelta(days=30)
        _, p_mb1 = get_nearest_trading_day(mb1_date, 'forward')
        
        # 1 month after (approx 30 days)
        ma1_date = edate + pd.Timedelta(days=30)
        _, p_ma1 = get_nearest_trading_day(ma1_date, 'backward')
        
        # 3 months after (approx 90 days)
        ma3_date = edate + pd.Timedelta(days=90)
        _, p_ma3 = get_nearest_trading_day(ma3_date, 'backward')
        
        # 6 months after (approx 180 days)
        ma6_date = edate + pd.Timedelta(days=180)
        _, p_ma6 = get_nearest_trading_day(ma6_date, 'backward')
        
        ret_1m_before = ((e_price / p_mb1) - 1) * 100 if p_mb1 else None
        ret_1m_after = ((p_ma1 / e_price) - 1) * 100 if p_ma1 else None
        ret_3m_after = ((p_ma3 / e_price) - 1) * 100 if p_ma3 else None
        ret_6m_after = ((p_ma6 / e_price) - 1) * 100 if p_ma6 else None
        
        results.append({
            'Date': edate_str,
            'Type': etype,
            'RulingWon': '与党勝利' if ewin else '与党敗北',
            '1M_Before': ret_1m_before,
            '1M_After': ret_1m_after,
            '3M_After': ret_3m_after,
            '6M_After': ret_6m_after
        })

    df_res = pd.DataFrame(results)

    periods = ['1ヶ月前 (1M Before)', '1ヶ月後 (1M After)', '3ヶ月後 (3M After)', '6ヶ月後 (6M After)']
    cols = ['1M_Before', '1M_After', '3M_After', '6M_After']

    fig = make_subplots(
        rows=2, cols=2, 
        subplot_titles=("衆院選 × 与党勝利", "衆院選 × 与党敗北", "参院選 × 与党勝利", "参院選 × 与党敗北"),
        horizontal_spacing=0.1,
        vertical_spacing=0.15
    )

    categories = [
        ('衆院選', '与党勝利', 1, 1),
        ('衆院選', '与党敗北', 1, 2),
        ('参院選', '与党勝利', 2, 1),
        ('参院選', '与党敗北', 2, 2)
    ]

    for etype, ewin, row, col in categories:
        subset = df_res[(df_res['Type'] == etype) & (df_res['RulingWon'] == ewin)]
        count = len(subset)
        
        means = []
        counts = []
        for c in cols:
            valid = subset[c].dropna()
            means.append(valid.mean() if not valid.empty else 0)
            counts.append(len(valid))
            
        colors = ['#00CC96' if val >= 0 else '#EF553B' for val in means]
        
        fig.add_trace(go.Bar(
            x=periods,
            y=means,
            marker_color=colors,
            text=[f"{m:+.2f}%" for m in means],
            textposition='auto',
            name=f"{etype} {ewin} (n={count})",
            hovertemplate="<b>%{x}</b><br>Avg Return: %{y:+.2f}%<extra></extra>",
            showlegend=False
        ), row=row, col=col)
        
        # Add summary text annotation
        fig.add_annotation(
            text=f"サンプル数: {count}回",
            xref="x domain", yref="y domain",
            x=0.05, y=0.95, showarrow=False,
            row=row, col=col,
            font=dict(size=12, color="gray")
        )

    fig.update_layout(
        title="日本株 国政選挙アノマリー (日経平均の選挙前後の平均騰落率)",
        template='plotly_dark',
        height=700
    )
    
    # Add zero lines
    fig.update_yaxes(zeroline=True, zerolinewidth=1, zerolinecolor='gray')
    
    fig.write_html(output_path)
    print(f"Election Anomaly chart successfully saved to {output_path}")

if __name__ == '__main__':
    create_election_anomaly_chart()
