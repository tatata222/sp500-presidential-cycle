import pandas as pd
import plotly.graph_objects as go
import numpy as np

fig = go.Figure()
# Box 1
fig.add_trace(go.Box(y=[1,2,3], name='B1'))
# Box 2 
fig.add_trace(go.Box(y=[2,3,4], name='B2'))
# Scatter 1
fig.add_trace(go.Scatter(y=[1,2,3], name='S1'))
# Scatter 2
fig.add_trace(go.Scatter(y=[2,3,4], name='S2'))

y_new = [[10, 20, 30], [20, 30, 40]]

fig.update_layout(
    updatemenus=[
        dict(
            type="dropdown",
            buttons=[
                dict(
                    label="Change",
                    method="restyle",
                    args=[{"y": y_new}, [2, 3]]
                )
            ]
        )
    ]
)
fig.write_html('test_restyle.html')
