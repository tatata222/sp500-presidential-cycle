import plotly.graph_objects as go
fig = go.Figure()

# trace 0: Box 1 (visible)
fig.add_trace(go.Box(y=[1,100,200], visible=True))
# trace 1: Scatter 1 (visible)
fig.add_trace(go.Scatter(y=[50,60,70], visible=True))

# trace 2: Box 2 (invisible)
fig.add_trace(go.Box(y=[1000, 2000, 3000], visible=False))
# trace 3: Scatter 2 (invisible)
fig.add_trace(go.Scatter(y=[1500, 1600, 1700], visible=False))

fig.update_layout(
    updatemenus=[
        dict(
            buttons=[
                # Use restyle instead of update to not override the entire trace dict
                dict(label='Period 1', method='restyle', args=[{'visible': [True, True, False, False]}]),
                dict(label='Period 2', method='restyle', args=[{'visible': [False, False, True, True]}])
            ], y = 1.2
        ),
        dict(
            buttons=[
                dict(label='Box On', method='restyle', args=[{'visible': True}, [0, 2]]),
                dict(label='Box Off', method='restyle', args=[{'visible': False}, [0, 2]])
            ]
        )
    ]
)
fig.write_html('test_box_orthogonal.html')
