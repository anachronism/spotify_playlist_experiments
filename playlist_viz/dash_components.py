from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plotly import tools 
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State
import dash_table

#fig1 = updateScatter3D(df_clustered,nPlaylists,None) # Plot all


# Given a dataframe that has the clusters, plot the plots.
def updateScatter3D(dfIn,nPlaylists,cFocus):
    # TODO re-add cFocus. Figure out how to make it efficient.

    line=dict(width=0.5,color='Black')
    marker = dict(size=2,color=dfIn["Cluster"],colorscale='Rainbow',line=line)
    data = go.Scatter3d(x=dfIn["x"],y=dfIn["y"],z=dfIn["z"], mode='markers',marker=marker)
    return go.Figure(data=[data])
