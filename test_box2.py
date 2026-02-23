import pandas as pd
import plotly.graph_objects as go
import numpy as np

month_ends = pd.date_range("2000-01-01", "2000-12-31", freq='ME')

# generate some cycle data
dates = list(month_ends.to_pydatetime()) * 10
cycles = ['C1'] * (12 * 10)
vals = np.random.randn(12 * 10) + 100

dates2 = list(month_ends.to_pydatetime()) * 10
cycles2 = ['C2'] * (12 * 10)
vals2 = np.random.randn(12 * 10) + 105

df = pd.DataFrame({'x': dates + dates2, 'y': np.concatenate([vals, vals2]), 'cycle': cycles + cycles2})

fig = go.Figure()

for c in ['C1', 'C2']:
    sub = df[df['cycle'] == c]
    fig.add_trace(go.Box(
        x=sub['x'], y=sub['y'], name=c, boxpoints=False # or 'outliers'
    ))

fig.update_layout(boxmode='group')
fig.write_html('test_box2.html')
