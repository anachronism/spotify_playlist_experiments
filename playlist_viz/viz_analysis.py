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
from model_fcns import dimReduce,runClustering
import utils 

import numpy as np
import pandas as pd
import seaborn as sns

sp = initSpotipy("playlist-modify-private")

projectDown = False
clusterData = False
chooseClusterNum = True
runPlot = True

nTableShow = 15

csv_folder = "playlist_csvs"
csv_folder_out = "output_playlists"
model_folder = "pkl_vals"

fid_poolRed = "/".join((model_folder,"poolReduced"))
fid_clustering = "/".join((model_folder,"clusters.pkl"))
fid_clusterNum = "/".join((model_folder,"nPlaylists"))
fid_totalPool =  "/".join((model_folder,"totalPool.pkl"))
fid_inputPkl = "/".join((model_folder,"crates_compiled.pkl"))

### TODO: add script to run through all csvs in folder.
#test_ex = "jul_2020_chance_encounters.csv"
rangeClusterSearch = [2950,3050] #Right now, personal sweet spot is in this range
nPlayExport = 5
playExportInterval = 10#6
crate_range = [1,2,3,4,5,6,7,9,10,11,12,13,15]#,11,12] #,12

featuresPull = ['Danceability','Energy','Speechiness','Acousticness'
                    ,'Instrumentalness','Liveness','Valence','Loudness','Tempo'] #'Key',,'Loudness','Tempo' ### TODO: scale loudness, tempo to uniform.
minMaxPlots = ["Acousticness","Danceability","Valence","Energy"]
    # Running index, probably inefficient.
playlistMax = dict()
playlistMin = dict()
nTrip = 0
maxVals = np.zeros(len(minMaxPlots))
minVals = np.ones(len(minMaxPlots))


###### APPLY DIM REDUCTION
if projectDown:
    # Read saved pickle file from crate_compile script.
    df_pool = pd.read_pickle(fid_inputPkl)
    # Apply preprocessing.        
    df_pool = df_pool.sample(frac=1)
    df_pool = df_pool[df_pool["Duration_ms"] > 30000]
    df_clust_pool = df_pool[featuresPull] 
    df_clust_pool = df_clust_pool.dropna(axis='rows')
    
    poolReduced = dimReduce(df_clust_pool,3)    
    fid_poolRed = fid_poolRed+"_3d"

    df_pool["x"] = poolReduced[:,0]
    df_pool["y"] = poolReduced[:,1]
    df_pool["z"] = poolReduced[:,2]
    
    np.save(fid_poolRed,poolReduced)
    df_pool.to_pickle(fid_totalPool)
else:
    fid_poolRed = fid_poolRed+"_3d"
    poolReduced = np.load(fid_poolRed+".npy")
    df_pool = pd.read_pickle(fid_totalPool) 

###### APPLY CLUSTERING
if clusterData:
    ## Clustering.
    if chooseClusterNum:
        df_clustered,nPlaylists = runClustering(df_pool,rangeClusterSearch,True)
    else:
        nPlaylists = np.load(fid_clusterNum+".npy")
        df_clustered,nPlaylists = runClustering(df_pool,nPlaylists,False)

    df_clustered.to_pickle(fid_clustering)
    np.save(fid_clusterNum,nPlaylists)
else:
    df_clustered= pd.read_pickle(fid_clustering)
    nPlaylists = np.load(fid_clusterNum+".npy")


## Draw playlists out
df_centers = df_clustered.groupby(['Cluster']).mean()
indsPlaylistsOut = utils.drawClusters(df_centers,nPlayExport)    
df_drawn = df_clustered[df_clustered['Cluster'].isin(indsPlaylistsOut)]

############### Get max and min values.
# plSave = []
# for ind in range(0,nPlaylistOut):

#     idxTest = np.where(df_clustered["Cluster"]==ind)
#     idxTest = idxTest[0]
#     playlistOut = df_pool.iloc[idxTest]
#     plSave.append(playlistOut) ### NOTE: This is probably nto the best way to deal with this but I'm lazy right now.

#     for ind_plots,val in enumerate(minMaxPlots):
#         playlistVals[ind_plots,ind] = playlistOut[val].mean(axis=0)
#         if playlistVals[ind_plots,ind] > maxVals[ind_plots]:
#             maxVals[ind_plots] = playlistVals[ind_plots,ind]
#             playlistMax[val] = ind
#         elif playlistVals[ind_plots,ind] < minVals[ind_plots]:
#             minVals[ind_plots] = playlistVals[ind_plots,ind] 
#             playlistMin[val] = ind
        
#     #playlistOut.to_csv("/".join((csv_folder_out,playName)))

# ## get plot values for max and min playlists.
# idxMin = list(playlistMin.values())
# idxMax = list(playlistMax.values()) 
# idxCategories = list(playlistMin.keys())
# categoriesMax = ["Max "+ s for s in idxCategories]
# categoriesMin = ["Min "+ s for s in idxCategories]
# idxCategories = categoriesMin+categoriesMax
# # print(idxCategories)
# idxMinMax = idxMin + idxMax
# minMaxClusterPos = [clusterPoints[x][:] for x in idxMinMax]
# minMaxColors = []
# for idx, clusterGroup in enumerate(minMaxClusterPos):
#     #print(minMaxClusterPos[idx])
#     minMaxColors = minMaxColors + [idxCategories[idx]]* len(clusterGroup)
#     # print(minMaxColors)

# #print(minMaxColors)
# minMaxClusterPos = [item for sublist in scatterClusters for item in sublist]
# minMaxClusterPos = np.stack(scatterClusters)
# ## Make plots



######################### The actual Vis part.
#sns.histplot(playlistDance)

## Histogram showing the track counts of the clusters
trackCounts = np.bincount(df_clustered["Cluster"])
trace3 = go.Histogram(x=trackCounts)

if runPlot:
    initStr = [str(i) for i in indsPlaylistsOut]
    nodeBoxInit = ", ".join(initStr)

    keys = ["Title","Artist","Album Name", "Tempo"]#
    df_display = df_clustered[keys]
    df_display = df_display.iloc[0:nTableShow]

    fig1 = updateScatter3D(df_clustered,nPlaylists,None) # Plot all
    fig2 = updateScatter3D(df_drawn,nPlaylists,None) # plot selected
    fig3 = go.Figure(data=trace3) # hist
    # fig4 = updateScatter3D(minMaxClusterPos,minMaxColors,len(idxMin),None,True) # plot extremes

    ## Dash experimentation#
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']#
    app = dash.Dash(__name__ ,external_stylesheets=external_stylesheets)

    app.layout = html.Div(children=[
        html.H1(children="Max's Crate Visualization"),
        dcc.Graph(
        id="histTotal",
        figure=fig3),
        html.Br(),
        html.H3(id="topLabel",children="3d scatterplot of songs, tvne dim reduction"),
        html.Div(style={'display':'flex'},
            children=[ 
                dcc.Graph(
                    id='scatterAll',
                    figure=fig1,
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
                            responsive=False
                        ),

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
        html.Div(id='nodeShowUpdate_1', style={'display': 'none'}),
        html.Div(id='nodeShowClick', style={'display': 'none'}),
        html.Div(id='nodeShowUpdate_0', style={'display': 'none'}),

        # html.Br(),
        # html.H3(id="nodeSelExtreme", children="Extremities: "),
        # html.Div(
        #     style={'display':'flex'},
        #     children=[        
        #         #html.Div( style={'width':'49%'},
        #             #     children = [
        #             #     dash_table.DataTable(
        #             #         id="plTable_extreme",
        #             #         style_cell={
        #             #         'whiteSpace': 'normal',
        #             #         'height': 'auto',
        #             #         'textAlign':'left'
        #             #         },
        #             #         columns=[{"name": i, "id": i} for i in df_display.columns],
        #             #         data=df_display.to_dict('records'),
        #             #     ),
        #             # ]),
        #         html.Div(children = [
        #                 dcc.Graph(
        #                     id='scatterExtreme',
        #                     figure=fig4,
        #                     responsive=False
        #                 ),

        #                 # html.Div(style={'display':'flex',
        #                 #                 'margin':'auto'},
        #                 #         children=[
        #                 #     dcc.Input(id="node-box",value=nodeBoxInit, type='text'),
        #                 #     html.Button(
        #                 #         ['Update'],
        #                 #         id='btnState',
        #                 #         n_clicks=0
        #                 #     ),
        #                 #     html.Button(
        #                 #         ['Save Playlists'],
        #                 #         id='playlistSaveBtn_2',
        #                 #         n_clicks=0
        #                 #     ),
        #                 #     html.Button(
        #                 #         ['Draw 5 Clusters'],
        #                 #         id='playlistDrawBtn',
        #                 #         n_clicks=0
        #                 #     ),
        #                 #     html.Div(id='plSaveOutput2')
        #                 # ]),
        #             ]),
            
        #     ]
        # ),
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
        fig = updateScatter3D(df_drawn,nPlaylists,None)

        return fig, nodePlot[0]


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
            sp = initSpotipy("playlist-modify-private")
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
            for ind in playlistInd:
                writeOut = df_clustered[df_clustered["Cluster"] == ind]
                sp = initSpotipy("playlist-modify-private")
                createPlaylist(sp,"Cluster "+str(ind),writeOut,True)

            return "Playlist Saved!"
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


    app.run_server(debug=True)




