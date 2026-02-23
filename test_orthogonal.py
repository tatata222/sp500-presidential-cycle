import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Box(y=[1,2,3], name='Box 1', visible=True, hoverinfo='all'))
fig.add_trace(go.Scatter(y=[1,2,3], name='Line 1', visible=True))

fig.add_trace(go.Box(y=[4,5,6], name='Box 2', visible=False, hoverinfo='all'))
fig.add_trace(go.Scatter(y=[4,5,6], name='Line 2', visible=False))

# Dropdown A: Period
fig.update_layout(
    updatemenus=[
        dict(
            buttons=[
                dict(label="Period 1", method="restyle", args=[{"visible": [True, True, False, False]}]),
                dict(label="Period 2", method="restyle", args=[{"visible": [False, False, True, True]}])
            ],
            y=1.2
        ),
        dict(
            buttons=[
                dict(label="Box On", method="restyle", args=[{"opacity": 1, "hoverinfo": "all"}, [0, 2]]),
                dict(label="Box Off", method="restyle", args=[{"opacity": 0, "hoverinfo": "skip"}, [0, 2]])
            ],
            y=1.1
        )
    ]
)
fig.write_html('test_orthogonal.html')
