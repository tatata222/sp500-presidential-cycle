import plotly.graph_objects as go

fig = go.Figure()

# For simplicity:
# Traces 0-3: Range 1 (0: Box, 1: Line)
# Traces 4-7: Range 2 (4: Box, 5: Line)

fig = go.Figure()
# Range 1
fig.add_trace(go.Box(y=[1,100,200], visible=False))       # T0
fig.add_trace(go.Scatter(y=[50,60,70], visible=True))     # T1
# Range 2
fig.add_trace(go.Box(y=[1000,2000,3000], visible=False))  # T2
fig.add_trace(go.Scatter(y=[1500,1600,1700], visible=False)) # T3

fig.update_layout(
    updatemenus=[
        dict(
            buttons=[
                # Period 1 ON (Line ON, Box depends on state, let's just say we don't touch box visible here?)
                # Wait, if we use opacity, the y-axis still auto-scales to include the invisible box!
                # If we use visibility, they might override each other.
                
                # What if Box and Line are in completely separate subplots? No, we need same axis.
            ]
        )
    ]
)
