import plotly.graph_objects as go
fig = go.Figure()

fig.add_trace(go.Box(y=[1,100,200], visible=False))       # T0 (Box Range 1)
fig.add_trace(go.Scatter(y=[50,60,70], visible=True))     # T1 (Line Range 1)

fig.add_trace(go.Box(y=[1000,2000,3000], visible=False))  # T2 (Box Range 2)
fig.add_trace(go.Scatter(y=[1500,1600,1700], visible=False)) # T3 (Line Range 2)

fig.update_layout(
    updatemenus=[
        dict(
            buttons=[
                # Use update instead of restyle for complex logic, or just visible.
                # If we ONLY update lines in Period selector... wait, if Period changes, we MUST hide the old Box/Line and SHOW the new Line.
                # What about the new Box? That depends on Box Toggle State.
                # But Plotly doesn't store variables.
                
                # So we can't completely decouple them via true `visible` state if they interact.
            ]
        )
    ]
)
