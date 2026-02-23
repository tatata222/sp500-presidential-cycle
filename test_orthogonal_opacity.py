import plotly.graph_objects as go
fig = go.Figure()
fig.add_trace(go.Box(y=[1,100, 200], visible=True, opacity=0))
fig.add_trace(go.Scatter(y=[50, 60, 70], visible=True, opacity=1))
fig.write_html('test_box_scale2.html')
