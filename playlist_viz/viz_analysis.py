# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 18:46:12 2021

@author: Max
TODO:
    proper interfacing with the spotify API.
    EDA on the subdivided groups.
    Proper Investigation on the different dimensionality reduction techniques.
    3d visualization, more interactive visualization.
    Look at genre groupings.
"""
#import plotly.express as px
import plotly
import plotly.graph_objects as go

from sklearn.cluster import SpectralClustering,DBSCAN,AgglomerativeClustering
from spotify_interactions import createPlaylist
from model_fcns import dimReduce

import numpy as np
import pandas as pd
import seaborn as sns


projectDown =True
clusterData = True
plot3D = True
writePlaylists = False
writeMaxPlaylists = True

csv_folder = "playlist_csvs"
csv_folder_out = "output_playlists"
model_folder = "pkl_vals"

fid_poolRed = "/".join((model_folder,"poolReduced"))
fid_clustering = "/".join((model_folder,"clusters"))
fid_totalPool =  "/".join((model_folder,"totalPool.pkl"))

### TODO: add script to run through all csvs in folder.
test_ex = "jul_2020_chance_encounters.csv"
nPlaylists = 150#6
nPlayExport = 5
playExportInterval = 1#6
crate_range = [6,7,9,10,11,12,13,15]#,11,12] #,12

minMaxPlots = ["Danceability","Valence","Energy"]
    # Running index, probably inefficient.
playlistVals = np.zeros((len(minMaxPlots),nPlaylists))
playlistMax = dict()
playlistMin = dict()
#playlistDance = np.zeros((nPlaylists,))
#playlistValence = np.zeros((nPlaylists,))
#playlistEnergy = np.zeros((nPlaylists,))

if projectDown:
    df_pool = pd.DataFrame()   
   
    for ind in crate_range:
        test_str = "_crate_"+str(ind)+"_.csv"
        fid_pool = "/".join((csv_folder,test_str))
        df_tmp = pd.read_csv(fid_pool)
        df_pool = df_pool.append(df_tmp)
    
    fid_ex = "/".join((csv_folder,test_ex))
    #df_pool = pd.read_csv(fid_pool)
    df_pool = df_pool.sample(frac=1)
    df_ex = pd.read_csv(fid_ex)
    print(df_pool.head())
    
    
    
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
    sc = AgglomerativeClustering(n_clusters = nPlaylists)
    # sc = DBSCAN(n_jobs=-1)
    splitVals = sc.fit_predict(poolReduced)
    np.save(fid_clustering,splitVals)
else:
    splitVals = np.load(fid_clustering+".npy")


nPlaylistOut = np.unique(splitVals).size
nTrip = 0
maxVals = np.zeros(len(minMaxPlots))
minVals = np.ones(len(minMaxPlots))

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
        
    playName = "playlist"+str(ind)+".csv"
    if nTrip < nPlayExport and writePlaylists and not ind % playExportInterval:
        nTrip = nTrip+1
        createPlaylist(playName,playlistOut)
    playlistOut.to_csv("/".join((csv_folder_out,playName)))

if writeMaxPlaylists:
    for val in minMaxPlots:
        createPlaylist("Maximum "+val,playlistMax[val])
        createPlaylist("Minimum "+val,playlistMin[val])

#sns.histplot(playlistDance)

if plot3D:
    plotly.offline.plot({
    "data": [
        go.Scatter3d(    x=poolReduced[:,0],
        y=poolReduced[:,1],z=poolReduced[:,2], mode='markers',#,
        marker=dict(
            size=5,color=splitVals,line=dict(width=2,
                                             color='DarkSlateGrey')),
        hovertemplate =
        '<i>X</i>: %{x:.2f}<br />'+
        '<i>Y</i>: %{y:.2f}<br />'+
        '<i>Z</i>: %{z:.2f}<br />'+
        '<i>Cluster</i>: %{marker.color:d}',)],
    "layout": plotly.graph_objs.Layout(showlegend=False,
        height=800,
        width=800,
    )
    })
else:
    plotly.offline.plot({
    "data": [
        go.Scatter(    x=poolReduced[:,0],
        y=poolReduced[:,1], mode='markers',#,
        marker=dict(
            size=5,color=splitVals),
        hovertemplate =
        '<i>X</i>: %{x:.2f}<br />'+
        '<i>Y</i>: %{y:.2f}<br />'+
        '<i>Cluster</i>: %{marker.color:d}',)],
    "layout": plotly.graph_objs.Layout(showlegend=False,
        height=800,
        width=800,
    )
    })
