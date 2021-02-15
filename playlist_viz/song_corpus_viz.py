# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 18:46:12 2021

@author: Max
NOTE: 
    I think that this stuff with dash is relatively jank, because of the inability to pass values out. 

TODO:
    CHANGE the plot sel thing in figure 1 to have each cluster a different trace, and change sicze of trace.
    All points tiny, include centers, size up the points that are active
    Dropdown menu to print out the min/max playlists
    EDA on the subdivided groups.
    Proper Investigation on the different dimensionality reduction techniques.
    Look at genre groupings.
    See if i can incorporate timbre patterns (12 dim vectors) (look into, see if can PCA down before later reduction).
"""
#import plotly.express as px

import json
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plotly import tools 
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State
import dash_table

from dash_components import updateScatter3D


from spotify_interactions import createPlaylist,initSpotipy
import utils 

import numpy as np
import pandas as pd

sp = initSpotipy("playlist-modify-private")

nTableShow = 15

model_folder = "pkl_vals"

fid_clustering_thresh = "/".join((model_folder,"clusters_thresh.pkl"))
fid_clustering = "/".join((model_folder,"clusters.pkl"))
fid_clusterNum = "/".join((model_folder,"nPlaylists"))

nPlayExport = 5
#minPlSize = 7 # minimum playlist size.

### Draw clusters to display
### having it draw only from the min pl size set in song_corpus_analysis at the moment.
df_clustered= pd.read_pickle(fid_clustering)
nPlaylists = np.load(fid_clusterNum+".npy")

df_clustered_thresh = pd.read_pickle(fid_clustering_thresh)
df_centers = df_clustered_thresh.groupby(['Cluster']).mean()
indsPlaylistsOut = utils.drawClusters(df_centers,nPlayExport)    
df_drawn = df_clustered_thresh[df_clustered_thresh['Cluster'].isin(indsPlaylistsOut)]

minMaxPlots = ["Acousticness","Danceability","Valence","Energy"]
df_min,df_max = utils.getExtrema(df_clustered_thresh,minMaxPlots,3)
df_extrema = df_min.append(df_max)

dropdownListExtrema = [{"label":"All","value":"All"}]

for val in minMaxPlots:
    tmp = {"label":val,"value":val}
    dropdownListExtrema.append(tmp)


######################### The actual Vis part.

#sns.histplot(playlistDance)

## Histogram showing the track counts of the clusters
trackCounts = np.bincount(df_clustered["Cluster"])
trace3 = go.Histogram(x=trackCounts)

initStr = [str(i) for i in indsPlaylistsOut]
nodeBoxInit = ", ".join(initStr)

keys = ["Title","Artist","Album Name", "Tempo"]#
df_display = df_clustered[keys]
df_display = df_display.iloc[0:nTableShow]

fig1 = updateScatter3D(df_clustered,nPlaylists,None) # Plot all
fig2 = updateScatter3D(df_drawn,nPlaylists,None) # plot selected
fig3 = go.Figure(data=trace3) # hist#
fig4 = updateScatter3D(df_extrema,nPlaylists,None) # plot extremes (Going to have to modify later)

## Dash experimentation#
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']#
app = dash.Dash(__name__ ,external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children="Max's Crate Visualization"),
    dcc.Graph(
    id="histTotal",
    figure=fig3),
    html.Br(),
    ### Plot 1
    html.H3(id="topLabel",children="3d scatterplot of songs, tvne dim reduction"),
    html.Div(style={'display':'flex'},
        children=[ 
            dcc.Graph(
                id='scatterAll',
                figure=fig1,
                # animate=True
              ),
            html.Div( style={'width':'49%'},
                    children = [
                    dash_table.DataTable(
                        id="plTable_sel",
                        style_cell={
                        'whiteSpace': 'normal',
                        'height': 'auto',
                        'textAlign':'left'
                        },
                        columns=[{"name": i, "id": i} for i in df_display.columns],
                        data=df_display.to_dict('records'),
                    ),
                        html.Button(
                            ['Save Playlist'],
                            id='playlistSaveBtn_1',
                            n_clicks=0
                        ),
                        html.Div(id='plSaveOutput')
                ]
            ),
            ]
    ),

    html.Br(),
    ### Plot 2
    html.H3(id="nodeSelSub", children="Subselection of clusters: "),
    html.Div(
        style={'display':'flex'},
        children=[        
            html.Div( style={'width':'49%'},
                    children = [
                    dash_table.DataTable(
                        id="plTable",
                        style_cell={
                        'whiteSpace': 'normal',
                        'height': 'auto',
                        'textAlign':'left'
                        },
                        columns=[{"name": i, "id": i} for i in df_display.columns],
                        data=df_display.to_dict('records'),
                    ),
                ]),
            html.Div(children = [
                    dcc.Graph(
                        id='scatterSel',
                        figure=fig2,
                        responsive=False,
                        # animate=True
                    ),

                    html.Br(),
                    html.Div(style={'display':'flex',
                                    'margin':'auto'},
                            children=[
                        dcc.Input(id="node-box",value=nodeBoxInit, type='text'),
                        html.Button(
                            ['Update'],
                            id='btnState',
                            n_clicks=0
                        ),
                        html.Button(
                            ['Save Playlists'],
                            id='playlistSaveBtn_2',
                            n_clicks=0
                        ),
                        html.Button(
                            ['Draw 5 Clusters'],
                            id='playlistDrawBtn',
                            n_clicks=0
                        ),
                        html.Div(id='plSaveOutput2')
                    ]),
                ]),
        
        ]
    ),
    html.Div(id='nodeShowClick', style={'display': 'none'}),
    html.Div(id='nodeShowUpdate_0', style={'display': 'none'}),
    html.Div(id='nodeShowUpdate_1', style={'display': 'none'}),
    html.Div(id='nodeShowUpdate_2', style={'display': 'none'}),

    html.Br(),
    html.H3(id="topLabel_extrema", children="Extremities: "),
    html.Div(
        style={'display':'flex'},
        children=[        
            html.Div( style={'width':'49%'},
                    children = [
                    dash_table.DataTable(
                        id="plTable_extreme",
                        style_cell={
                        'whiteSpace': 'normal',
                        'height': 'auto',
                        'textAlign':'left'
                        },
                        columns=[{"name": i, "id": i} for i in df_display.columns],
                        data=df_display.to_dict('records'),
                    ),
                ]),
            html.Div(children = [
                    dcc.Graph(
                        id='scatterExtreme',
                        figure=fig4,
                        responsive=False
                    ),

                    html.Div(style={'display':'flex',
                                    'margin':'auto'},
                            children=[
                    #     dcc.Input(id="node-box",value=nodeBoxInit, type='text'),
                        dcc.Dropdown(
                            id='dropdownExtrema',
                            options=dropdownListExtrema,
                            value='All',
                            clearable=False,
                            searchable=False,
                            style={'width':'100%'}
                        ),
                        html.Button(
                            ['Save Playlists'],
                            id='playlistSaveBtn_3',
                            n_clicks=0
                        ),
                        html.Div(id='plSaveOutput3')

                    #     html.Button(
                    #         ['Draw 5 Clusters'],
                    #         id='playlistDrawBtn',
                    #         n_clicks=0
                    #     ),
                    #     html.Div(id='plSaveOutput2')
                    ]),
                ]),
        
        ]
    ),
    # dcc.Graph(
    #     id = "currPlaylistTable",
    #     figure = generateTable(df_display,max_rows=30)
    # )
])


################################### Callbacks
# Cluster sel update plot. 
@app.callback(
    Output('scatterSel', 'figure'),
    Output('nodeShowUpdate_1','children'),
#    Output('plTable', 'data'),
    Input('btnState','n_clicks'),
    State('node-box', 'value'))
def updateClusterSel(n_clicks,nodeStrIn):
    
    nodePlot = utils.parseNodeInputStr(nodeStrIn,nPlaylists)   
    df_drawn = df_clustered[df_clustered['Cluster'].isin(nodePlot)]
   # print(indsColor)
    
#    print (indsColor_loc)
   # print(nodePlot)
    fig = updateScatter3D(df_drawn,nPlaylists,None)
    return fig, nodePlot[0]


@app.callback(
    Output('plTable_extreme','data'),
    Input('nodeShowUpdate_2','children') ####HERE
    )
def updateTableAll(nodeShowUpdate):

    keys = ["Title","Artist","Album Name", "Tempo", "Key"]
    playlistOut = df_clustered[df_clustered["Cluster"] == nodeShowUpdate]
    playlistOut = playlistOut.iloc[0:nTableShow]
    df_display = playlistOut[keys].to_dict('records')

    return df_display

@app.callback(
    Output('scatterAll','figure'),
    Output('plTable_sel','data'),
    Input('nodeShowUpdate_0','children') ####HERE
    )
def updateTableAll(nodeShowUpdate):
    fig = updateScatter3D(df_clustered,nPlaylists,nodeShowUpdate)

    keys = ["Title","Artist","Album Name", "Tempo", "Key"]
    playlistOut = df_clustered[df_clustered["Cluster"] == nodeShowUpdate]
    playlistOut = playlistOut.iloc[0:nTableShow]
    df_display = playlistOut[keys].to_dict('records')

    return fig, df_display



@app.callback(
    Output('plTable','data'),
    Output('nodeSelSub','children'),
    Input('nodeShowUpdate_1','children'),
    Input('nodeShowClick','children')
    )
def updateTableSmall2(nodeShowUpdate,nodeShowClick):
    ctx = dash.callback_context
    trigID = ctx.triggered[0]['prop_id'].split('.')[0]
    print(trigID)

    if trigID == 'nodeShowUpdate_1':
        indUse = nodeShowUpdate
    else:
        indUse = nodeShowClick

    keys = ["Title","Artist","Album Name", "Tempo", "Key"]
    playlistOut = df_clustered[df_clustered["Cluster"] == indUse]
    playlistOut = playlistOut.iloc[0:nTableShow]
    df_display = playlistOut[keys].to_dict('records')


    headerLabel = "Subselection of clusters: " + str(indUse)

    return df_display,headerLabel

#Playlist saving callback    

#Playlist saving callback    
@app.callback(
    Output(component_id='plSaveOutput', component_property='children'), 
    Input('playlistSaveBtn_1','n_clicks'),
    State('nodeShowUpdate_0','children'))
def saveCurrentPlaylist(n_clicks,nodeIn):

  #  playlistInd = utils.parseNodeInputStr(nodeStrIn,nPlaylists)
  #  playlistInd = playlistInd[0]

    if n_clicks != 0:
        writeOut = df_clustered[df_clustered["Cluster"] == nodeIn]
      #  sp = initSpotipy("playlist-modify-private")
        createPlaylist(sp,"Cluster "+str(nodeIn),writeOut,True)

        return "Playlist Saved!"
    else:
        return "Init"

@app.callback(
    Output(component_id='plSaveOutput2', component_property='children'), 
    Input('playlistSaveBtn_2','n_clicks'),
    State('node-box','value'))
def savePlaylistsCluster(n_clicks,nodeStrIn):

    playlistInd = utils.parseNodeInputStr(nodeStrIn,nPlaylists)
  #  playlistInd = playlistInd[0]

    if n_clicks != 0:
#    print("Playlist ind! "+ boxValStr)
        sp = initSpotipy("playlist-modify-private")
        for ind in playlistInd:
            writeOut = df_clustered[df_clustered["Cluster"] == ind]
            createPlaylist(sp,"Cluster "+str(ind),writeOut,True)

        return "Playlist Saved!"
    else:
        return "Init"

@app.callback(
    Output(component_id='plSaveOutput3', component_property='children'), 
    Input('playlistSaveBtn_3','n_clicks'),
    State('dropdownExtrema','value'))
def savePlaylistsExtrema(n_clicks,nodeStrIn):

    if n_clicks != 0:
#    print("Playlist ind! "+ boxValStr)
       # sp = initSpotipy("playlist-modify-private")
        if nodeStrIn == "All":
            for elt in minMaxPlots:
                df_out= df_extrema[df_extrema["Category"]==elt]
                df_out_max = df_out[df_out["Extrema"] == "Max"]
                df_out_min = df_out[df_out["Extrema"] == "Min"]
                createPlaylist(sp,"Max %s | Cluster %d"%(elt,df_out_max.iloc[0]["Cluster"]),df_out_max,True)
                createPlaylist(sp,"Min %s | Cluster %d"%(elt,df_out_min.iloc[0]["Cluster"]),df_out_min,True)
        else:
            df_out= df_extrema[df_extrema["Category"]==nodeStrIn]
            df_out_max = df_out[df_out["Extrema"] == "Max"]
            df_out_min = df_out[df_out["Extrema"] == "Min"]
            createPlaylist(sp,"Max %s | Cluster %d"%(nodeStrIn,df_out_max.iloc[0]["Cluster"]),df_out_max,True)
            createPlaylist(sp,"Min %s | Cluster %d"%(nodeStrIn,df_out_min.iloc[0]["Cluster"]),df_out_min,True)

        return "Playlists Saved!"
    else:
        return "Init"


#Playlist saving callback    
@app.callback(
    Output('node-box','value'),
    Output('btnState','n_clicks'),
    Input('playlistDrawBtn','n_clicks'))
def drawMoreClusters(n_clicks):
    if n_clicks != 0:
        indsPlaylistsOut = utils.drawClusters(df_centers,nPlayExport)    
        initStr = [str(i) for i in indsPlaylistsOut]

        return ", ".join(initStr) , 1
    else:
        return nodeBoxInit,0

@app.callback(
    Output('topLabel_extrema', 'children'),
#    Output('plTable_sel', 'data'),
    Output('nodeShowUpdate_2','children'),
    Input('scatterExtreme', 'clickData'))
def display_click_data(clickData):
#    print(clickData)
    if not clickData is None:
        retPrint = clickData["points"][0]["marker.color"]
        idxUse = retPrint 
    else:
        retPrint = None
        idxUse = 0
    strPrint = "Extrema: " + str(idxUse)
    return strPrint,idxUse

@app.callback(
    Output('topLabel', 'children'),
#    Output('plTable_sel', 'data'),
    Output('nodeShowUpdate_0','children'),
    Input('scatterAll', 'clickData'))
def display_click_data(clickData):
#    print(clickData)
    if not clickData is None:
        retPrint = clickData["points"][0]["marker.color"]
        idxUse = retPrint 
    else:
        retPrint = None
        idxUse = 0
 
    # keys = ["Title","Artist","Album Name", "Tempo", "Key"]
    # playlistOut = plSave[idxUse] ### TODO: think about how I want to print these tables out. Maybe on tabs?
    # playlistOut = playlistOut.iloc[0:nTableShow]
    # df_display = playlistOut[keys].to_dict('records')

    strPrint = "Crate selected: " + str(idxUse)
    return strPrint,idxUse#df_display


@app.callback(
    Output('nodeShowClick', 'children'),
    Input('scatterSel', 'clickData'))
def display_click_data_subset(clickData):
#    print(clickData)
    if not clickData is None:
        retPrint = clickData["points"][0]["marker.color"]
        idxUse = retPrint 
    else:
        retPrint = None
        idxUse = 0
 
    return idxUse
#     return str(retPrint),df_display


@app.callback(
    Output('scatterExtreme','figure'),
    Input('dropdownExtrema','value'))
def display_sel_extrema(extremeIn):
    if extremeIn=="All":
        df_use = df_extrema
    else:
        df_use = df_extrema[df_extrema["Category"] == extremeIn]
    return updateScatter3D(df_use,nPlaylists,None)

app.run_server(debug=True)




