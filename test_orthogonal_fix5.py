import plotly.graph_objects as go
fig = go.Figure()

# To handle multiple dropdowns that change "visibility" we need a single JS state, which Plotly does NOT have easily via simple updatemenus if they are completely independent.
# BUT we can just overwrite the 'y' array of the box plots with an array of None or NaNs when we want to turn it "off".
# If y is None, it doesn't render and doesn't affect autorange!
# Then when we turn it "on", we reset it to the original y values.
# Is this possible?
# Let's test restyling a trace's 'y' data without touching visibility.

y_on = [[1, 100, 200], [1000, 2000, 3000]]
y_off = [[None, None, None], [None, None, None]]

fig.add_trace(go.Box(y=y_on[0], visible=True))
fig.add_trace(go.Box(y=y_on[1], visible=True))

fig.update_layout(
    updatemenus=[
        dict(
            buttons=[
                dict(label='Box On', method='restyle', args=[{'y': y_on}, [0, 1]]),
                dict(label='Box Off', method='restyle', args=[{'y': y_off}, [0, 1]])
            ]
        )
    ]
)
fig.write_html('test_box_nans.html')
