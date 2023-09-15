import plotly.graph_objects as go

import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Define the surface data
surface = go.Surface(z=[[1, 1, 1], [2, 2, 2], [3, 3, 3]])

# Define the color for each part of the surface
surface.facecolor = [
    ['rgb(255, 0, 0)', 'rgb(0, 255, 0)', 'rgb(0, 0, 255)'],
    ['rgb(255, 255, 0)', 'rgb(255, 0, 255)', 'rgb(0, 255, 255)'],
    ['rgb(127, 127, 127)', 'rgb(255, 255, 255)', 'rgb(0, 0, 0)']
]

# Create the figure and add the surface trace
fig = go.Figure(data=surface)


fig.write_html('C:/Users/User/Desktop/1.html')