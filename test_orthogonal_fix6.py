import pandas as pd
import plotly.graph_objects as go
fig = go.Figure()

df1 = pd.DataFrame({'x': [1,2,3], 'y': [1, 100, 200]})
y_null1 = [None, None, None]

df2 = pd.DataFrame({'x': [1,2,3], 'y': [1000, 2000, 3000]})
y_null2 = [None, None, None]

fig.add_trace(go.Box(x=df1['x'], y=df1['y'], visible=True))
fig.add_trace(go.Box(x=df2['x'], y=df2['y'], visible=True))

fig.update_layout(
    updatemenus=[
        dict(
            buttons=[
                dict(label='Box On', method='restyle', args=[{'y': [df1['y'].values, df2['y'].values]}, [0, 1]]),
                dict(label='Box Off', method='restyle', args=[{'y': [y_null1, y_null2]}, [0, 1]])
            ]
        )
    ]
)
fig.write_html('test_box_nans2.html')
