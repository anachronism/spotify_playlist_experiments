# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 18:46:12 2021

@author: Max
NOTE: 
    I think that this stuff with dash is relatively jank, because of the inability to pass values out. 

TODO:
    EDA on the subdivided groups.
    Proper Investigation on the different dimensionality reduction techniques.
    Look at genre groupings.
    See if i can incorporate timbre patterns (12 dim vectors) (look into, see if can PCA down before later reduction).
"""
#import plotly.express as px

from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plotly import tools 
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State
import dash_table

from dash_components import generateTable


from sklearn.cluster import SpectralClustering,OPTICS,AgglomerativeClustering,MiniBatchKMeans
from spotify_interactions import createPlaylist,initSpotipy
from model_fcns import dimReduce
import utils 

import numpy as np
import pandas as pd
import seaborn as sns


usePklInput = True
projectDown =False
clusterData = False
plot3D = True
writePlaylists = False
writeMaxPlaylists = False

dashPlot = True

nTableShow = 15

if writePlaylists or writeMaxPlaylists:
    sp = initSpotipy("playlist-modify-private")

if plot3D:
    nDims = 3
else:
    nDims = 2

csv_folder = "playlist_csvs"
csv_folder_out = "output_playlists"
model_folder = "pkl_vals"

fid_poolRed = "/".join((model_folder,"poolReduced"))
fid_clustering = "/".join((model_folder,"clusters"))
fid_totalPool =  "/".join((model_folder,"totalPool.pkl"))
fid_inputPkl = "/".join((model_folder,"crates_compiled.pkl"))

### TODO: add script to run through all csvs in folder.
#test_ex = "jul_2020_chance_encounters.csv"
nPlaylists = 450#150#6
nPlayExport = 5
playExportInterval = 10#6
crate_range = [1,2,3,4,5,6,7,9,10,11,12,13,15]#,11,12] #,12
#crate_range = [9,10,11,12,13,15]#,11,12] #,12

minMaxPlots = ["Acousticness","Danceability","Valence","Energy"]
    # Running index, probably inefficient.
playlistVals = np.zeros((len(minMaxPlots),nPlaylists))
clusterPos = np.zeros((nPlaylists,nDims))
playlistMax = dict()
playlistMin = dict()
nTrip = 0
maxVals = np.zeros(len(minMaxPlots))
minVals = np.ones(len(minMaxPlots))

if projectDown:
    df_pool = pd.DataFrame()   
   
    if usePklInput:
        df_pool = pd.read_pickle(fid_inputPkl)

    else:
        for ind in crate_range:
            test_str = "_crate_"+str(ind)+"_.csv"
            fid_pool = "/".join((csv_folder,test_str))
            df_tmp = pd.read_csv(fid_pool)
            df_pool = df_pool.append(df_tmp)
        
    df_pool = df_pool.sample(frac=1)
    df_pool = df_pool[df_pool["Duration_ms"] > 30000]
    #print(df_pool.head())

    featuresPull = ['Danceability','Energy','Speechiness','Acousticness'
                    ,'Instrumentalness','Liveness','Valence','Loudness','Tempo'] #'Key',,'Loudness','Tempo' ### TODO: scale loudness, tempo to uniform.
    df_clust_pool = df_pool[featuresPull]
    df_clust_pool = df_clust_pool.dropna(axis='rows')
    
    if plot3D:
        poolReduced = dimReduce(df_clust_pool,3)    
        fid_poolRed = fid_poolRed+"_3d"
    else:
        poolReduced = dimReduce(df_clust_pool,2)

    np.save(fid_poolRed,poolReduced)
    df_pool.to_pickle(fid_totalPool)
else:
    if plot3D:
        fid_poolRed = fid_poolRed+"_3d"

    poolReduced = np.load(fid_poolRed+".npy")
    df_pool =pd.read_pickle(fid_totalPool) 

if clusterData:
    ## Clustering.
    #sc = SpectralClustering(n_clusters = nPlaylists,n_jobs=-1)
    #sc = AgglomerativeClustering(n_clusters = nPlaylists) # ward linkage
    sc = MiniBatchKMeans(n_clusters = nPlaylists)
    #sc = OPTICS(min_samples=100,n_jobs=-1)
    splitVals = sc.fit_predict(poolReduced)
    np.save(fid_clustering,splitVals)
    # sns.histplot(splitVals,bins=nPlaylists)
else:
    splitVals = np.load(fid_clustering+".npy")

nPlaylistOut = np.min([np.unique(splitVals).size,nPlaylists])
## Distance calculation and such.
clusterPoints = [] # separately saved points
clusterInds = []
for ind in range(0,nPlaylistOut):
    idxTest = np.where(splitVals==ind)
    idxTest = idxTest[0]
    posSave = poolReduced[idxTest,:] 
    clusterPoints.append(posSave)
    clusterInds.append([ind]* posSave.shape[0])

    clusterPos[ind,:] = np.mean(posSave,axis=0)



indPlaylistsOut,clusterCenters = utils.drawClusters(clusterPos,nPlayExport)    

scatterClusters = [clusterPoints[x] for x in indPlaylistsOut]
scatterClusters = [item for sublist in scatterClusters for item in sublist]
scatterClusters = np.stack(scatterClusters)

indsScatter = [clusterInds[x] for x in indPlaylistsOut]
indsScatter = [item for sublist in indsScatter for item in sublist]

initArray = np.unique(indsScatter)
initStr = [str(i) for i in initArray]
nodeBoxInit = ", ".join(initStr)

plSave = []
## Write playlists out
for ind in range(0,nPlaylistOut):

    idxTest = np.where(splitVals==ind)
    idxTest = idxTest[0]
    playlistOut = df_pool.iloc[idxTest]
    plSave.append(playlistOut) ### NOTE: This is probably nto the best way to deal with this but I'm lazy right now.

    for ind_plots,val in enumerate(minMaxPlots):
        playlistVals[ind_plots,ind] = playlistOut[val].mean(axis=0)
        if playlistVals[ind_plots,ind] > maxVals[ind_plots]:
            maxVals[ind_plots] = playlistVals[ind_plots,ind]
            playlistMax[val] = playlistOut
        elif playlistVals[ind_plots,ind] < minVals[ind_plots]:
            minVals[ind_plots] = playlistVals[ind_plots,ind] 
            playlistMin[val] = playlistOut
        
    playName = "playlist"+str(ind)+ " kMeans"+".csv"
    if ind in indPlaylistsOut and writePlaylists:
        createPlaylist(sp,playName,playlistOut,True)
    
    #playlistOut.to_csv("/".join((csv_folder_out,playName)))

if writeMaxPlaylists:
    for val in minMaxPlots:
        createPlaylist(sp,"Maximum "+val + " kMeans",playlistMax[val],True)
        createPlaylist(sp,"Minimum "+val+ " kMeans",playlistMin[val],True)

## Make plots
######################### The actual Vis part.
#sns.histplot(playlistDance)
if plot3D:
    
    trace1 =go.Scatter3d(    x=poolReduced[:,0],
        y=poolReduced[:,1],z=poolReduced[:,2], mode='markers',#,
        marker=dict(
            size=5,color=splitVals,colorscale="Rainbow",line=dict(width=2,
                                             color='DarkSlateGrey')),
        hovertemplate =
        '<i>X</i>: %{x:.2f}<br />'+
        '<i>Y</i>: %{y:.2f}<br />'+
        '<i>Z</i>: %{z:.2f}<br />'+
        '<i>Cluster</i>: %{marker.color:d}',
        )
    trace2 = go.Scatter3d(    x=scatterClusters[:,0],
        y=scatterClusters[:,1],z=scatterClusters[:,2], mode='markers',#,
        marker=dict(
            size=5,color=indsScatter,colorscale="Rainbow",line=dict(width=2,
                                             color='DarkSlateGrey')),
        hovertemplate =
        '<i>X</i>: %{x:.2f}<br />'+
        '<i>Y</i>: %{y:.2f}<br />'+
        '<i>Z</i>: %{z:.2f}<br />'+
        '<i>Cluster</i>: %{marker.color:d}',
        )

else:
    trace1 = go.Scatter(    x=poolReduced[:,0],
        y=poolReduced[:,1], mode='markers',#,
        marker=dict(
            size=5,color=splitVals),
        hovertemplate =
        '<i>X</i>: %{x:.2f}<br />'+
        '<i>Y</i>: %{y:.2f}<br />'+
        '<i>Cluster</i>: %{marker.color:d}',
        color="Alphabet",opacity=0)
    trace2 = go.Scatter(    x=scatterClusters[:,0],
        y=scatterClusters[:,1], mode='markers',#,
        marker=dict(
            size=100,color=indsScatter),
        hovertemplate =
        '<i>X</i>: %{x:.2f}<br />'+
        '<i>Y</i>: %{y:.2f}<br />'+
        '<i>Cluster</i>: %{marker.color:d}',
        color="Alphabet")

#trace3 = go.Histogram(x=splitVals,xbins = dict(size=1),xaxis="x2",
 #                 yaxis="y2")

trackCounts = np.bincount(splitVals)
trace3 = go.Histogram(x=trackCounts)

layout1 = go.Layout(
    scene1 = dict(
        xaxis = dict(nticks=4, range=[-40,40],),
        yaxis = dict(nticks=4, range=[-40,40],),
        zaxis = dict(nticks=4, range=[-40,40],),
    ),
    scene2 = dict(
        xaxis = dict(nticks=4, range=[-40,40],),
        yaxis = dict(nticks=4, range=[-40,40],),
        zaxis = dict(nticks=4, range=[-40,40],),
    ),
    width=1000,
    margin=dict(r=10, l=10, b=10, t=10),showlegend=False
)


layout2 = go.Layout(
    showlegend = False,
    width=500
)


markdown_text = '''
### Track Count:
'''
keys = ["Title","Artist","Album Name", "Tempo"]#
df_display = playlistOut[keys]
df_display = df_display.iloc[0:nTableShow]


fig1 = make_subplots(rows=1, cols=2,specs=[[{'type': 'surface'}, {'type': 'bar'}]])#
fig1.add_trace(trace1,row=1,col=1)#
fig1.add_trace(trace3,row=1,col=2)
fig1.update_layout(layout1)


#fig1 = go.Figure(data=trace1,layout=layout1)
fig2 = go.Figure(data=trace2,layout=layout2)
#fig3 = go.Figure(data=trace3,layout=layout2)

#fig1.show(renderer='browser')
varTest = 0
#print("test" + str(varTest))
sliderNotches = range(nPlaylists)
sliderNotches = sliderNotches[0::20]
## Dash experimentation#
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']#
app = dash.Dash(__name__ ,external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children="Max's Crate Visualization"),
    html.Label("3d scatterplot of songs, tvne dim reduction"),
    dcc.Graph(
        id='scatterAll',
        figure=fig1,
    ),
    html.Br(),

    dcc.Markdown(children=markdown_text),
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
                            ['Save Playlist'],
                            id='playlistSaveBtn',
                            n_clicks=0
                        ),
                        html.Button(
                            ['Draw 5 Clusters'],
                            id='playlistDrawBtn',
                            n_clicks=0
                        ),
                        html.Div(id='plSaveOutput')
                    ]),
                ]),
        
        ]
    ),
    

    # dcc.Graph(
    #     id = "currPlaylistTable",
    #     figure = generateTable(df_display,max_rows=30)
    # )
])


# Cluster sel update plot. 

@app.callback(
    Output('scatterSel', 'figure'),
    Output('plTable', 'data'),
    Input('btnState','n_clicks'),
    State('node-box', 'value'))
def updateClusterSel(n_clicks,nodeStrIn):
    
    nodePlot = utils.parseNodeInputStr(nodeStrIn,nPlaylists)   
    pointsScatter = [clusterPoints[nodeInd] for nodeInd in nodePlot]
    pointsScatter = np.array([item for sublist in pointsScatter for item in sublist]) # Flatten list
    
    indsColor = [clusterInds[nodeInd] for nodeInd in nodePlot]
    indsColor = [item for sublist in indsColor for item in sublist]
   # print(indsColor)
    
    traceUse = go.Scatter3d( x=pointsScatter[:,0],
        y=pointsScatter[:,1],z=pointsScatter[:,2], mode='markers',#,
        marker=dict(
            size=5,color=indsColor,colorscale="Rainbow",cmin=0,cmax=nPlaylists-1,line=dict(width=2,
                                             color='DarkSlateGrey')),
        hovertemplate =
        '<i>X</i>: %{x:.2f}<br />'+
        '<i>Y</i>: %{y:.2f}<br />'+
        '<i>Z</i>: %{z:.2f}<br />'+
        '<i>Cluster</i>: %{marker.color: 3d}',
    )
    

    layoutUse = go.Layout(
        scene1 = dict(
            xaxis = dict(nticks=4, range=[-40,40],),
            yaxis = dict(nticks=4, range=[-40,40],),
            zaxis = dict(nticks=4, range=[-40,40],),
        ),
        scene2 = dict(
            xaxis = dict(nticks=4, range=[-40,40],),
            yaxis = dict(nticks=4, range=[-40,40],),
            zaxis = dict(nticks=4, range=[-40,40],),
        ),
        width=1000,
        margin=dict(r=10, l=10, b=10, t=10),showlegend=False
    )
    fig = go.Figure(data=traceUse,layout=layoutUse)

    keys = ["Title","Artist","Album Name", "Tempo", "Key"]
    playlistOut = plSave[nodePlot[0]] ### TODO: think about how I want to print these tables out. Maybe on tabs?
    playlistOut = playlistOut.iloc[0:nTableShow]

    df_display = playlistOut[keys].to_dict('records')
    return fig,df_display


#Playlist saving callback    
@app.callback(
    Output(component_id='plSaveOutput', component_property='children'), 
    Input('playlistSaveBtn','n_clicks'),
    State('node-box','value'))
def saveCurrentPlaylist(n_clicks,nodeStrIn):

    playlistInd = utils.parseNodeInputStr(nodeStrIn,nPlaylists)
  #  playlistInd = playlistInd[0]

    if n_clicks != 0:
#    print("Playlist ind! "+ boxValStr)
        for ind in playlistInd:
            writeOut = plSave[ind]
            sp = initSpotipy("playlist-modify-private")
            createPlaylist(sp,"Cluster "+str(ind),writeOut,True)

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
        indPlaylistsOut,clusterCenters = utils.drawClusters(clusterPos,nPlayExport)    

        scatterClusters = [clusterPoints[x] for x in indPlaylistsOut]
        scatterClusters = [item for sublist in scatterClusters for item in sublist]
        scatterClusters = np.stack(scatterClusters)

        indsScatter = [clusterInds[x] for x in indPlaylistsOut]
        indsScatter = [item for sublist in indsScatter for item in sublist]

        indsPrint = np.unique(indsScatter)
        initStr = [str(i) for i in indsPrint]
     #  print(", ".join(initStr))
        return ", ".join(initStr) , 1
    else:
        return nodeBoxInit,0
app.run_server(debug=True)




