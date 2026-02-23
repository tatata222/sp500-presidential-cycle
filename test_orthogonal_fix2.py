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
                dict(label='Period 1', method='restyle', args=[
                    {'visible': [
                        True,  # T0 Box 1
                        True,  # T1 Scatter 1
                        False, # T2 Box 2
                        False  # T3 Scatter 2
                    ]}
                ]),
                dict(label='Period 2', method='restyle', args=[
                    {'visible': [
                        False, # T0 Box 1
                        False, # T1 Scatter 1
                        True,  # T2 Box 2
                        True   # T3 Scatter 2
                    ]}
                ])
            ], y=1.2
        ),
        dict(
            buttons=[
                dict(label='Box On', method='restyle', args=[{'visible': True}, [0, 2]]),
                dict(label='Box Off', method='restyle', args=[{'visible': False}, [0, 2]])
            ]
        )
    ]
)
fig.write_html('test_orthogonal_fix3.html')
