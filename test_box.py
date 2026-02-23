import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Let's say we have normalized prices for 3 years
# for random days.
df = pd.DataFrame({
    'Normalized_Price': np.random.randn(100) + 100,
    'Date': pd.date_range('2000-01-01', periods=100)
})

fig = go.Figure()
fig.add_trace(go.Scatter(x=df['Date'], y=df['Normalized_Price'], mode='lines'))
fig.add_trace(go.Box(x=df['Date'].dt.to_period('M').dt.to_timestamp('M'), y=df['Normalized_Price'], name='Box'))
fig.write_html('test_box.html')
