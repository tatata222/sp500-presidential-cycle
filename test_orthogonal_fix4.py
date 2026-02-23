import plotly.graph_objects as go
fig = go.Figure()

fig.add_trace(go.Box(y=[1,100,200], visible=False))       # T0 (Box Range 1)
fig.add_trace(go.Scatter(y=[50,60,70], visible=True))     # T1 (Line Range 1)

fig.add_trace(go.Box(y=[1000,2000,3000], visible=False))  # T2 (Box Range 2)
fig.add_trace(go.Scatter(y=[1500,1600,1700], visible=False)) # T3 (Line Range 2)

fig.update_layout(
    yaxis=dict(autorange=True),
    updatemenus=[
        dict(
            buttons=[
                dict(label='Period 1', method='update', args=[
                    {'visible': [
                        True,  # T0 Box 1
                        True,  # T1 Scatter 1
                        False, # T2 Box 2
                        False  # T3 Scatter 2
                    ]},
                    {'yaxis.autorange': True}
                ]),
                dict(label='Period 2', method='update', args=[
                    {'visible': [
                        False, # T0 Box 1
                        False, # T1 Scatter 1
                        True,  # T2 Box 2
                        True   # T3 Scatter 2
                    ]},
                    {'yaxis.autorange': True}
                ])
            ], y=1.2
        ),
        dict(
            buttons=[
                dict(label='Box On', method='restyle', args=[
                    {'visible': True}, [0, 2] # This will turn ON both Box 1 and Box 2. But we just set Box 2 invisible in Period 1!
                ]),
                dict(label='Box Off', method='restyle', args=[
                    {'visible': False}, [0, 2]
                ])
            ]
        )
    ]
)
