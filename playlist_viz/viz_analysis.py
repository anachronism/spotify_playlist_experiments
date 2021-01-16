# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 18:46:12 2021

@author: Max
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
nPlayExport = 15
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


## Write playlists out
for ind in range(0,nPlaylistOut):

    idxTest = np.where(splitVals==ind)
    idxTest = idxTest[0]
    playlistOut = df_pool.iloc[idxTest]

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
    playlistOut.to_csv("/".join((csv_folder_out,playName)))

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

trace3 = go.Histogram(x=splitVals,xbins = dict(size=1),xaxis="x2",
                  yaxis="y2")


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


fig1 = make_subplots(rows=1, cols=2,specs=[[{'type': 'surface'}, {'type': 'surface'}]])
fig1.add_trace(trace1,row=1,col=1)
fig1.add_trace(trace2,row=1,col=2)
fig1.update_layout(layout1)
fig2 = go.Figure(data=trace3,layout=layout2)

#fig1.show(renderer='browser')

## Dash experimentation
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#external_stylesheets=external_stylesheets
app = dash.Dash(__name__ )

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),
    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    dcc.Graph(
        id='scatters',
        figure=fig1
    ),
    dcc.Graph(
        id='hist',
        figure=fig2
    ),
    generateTable(playlistOut)
])

app.run_server(debug=True)




