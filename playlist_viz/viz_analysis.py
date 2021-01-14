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
import plotly.graph_objs

from sklearn.cluster import SpectralClustering,DBSCAN,AgglomerativeClustering
from spotify_interactions import createPlaylist
from model_fcns import dimReduce

import numpy as np
import pandas as pd
import seaborn as sns


projectDown = False
writePlaylists = False

csv_folder = "playlist_csvs"
csv_folder_out = "output_playlists"
model_folder = "pkl_vals"

fid_poolRed = "/".join((model_folder,"poolReduced"))
fid_totalPool =  "/".join((model_folder,"totalPool.pkl"))

### TODO: add script to run through all csvs in folder.
test_ex = "jul_2020_chance_encounters.csv"
nPlaylists = 150#6
nPlayExport = 5
crate_range = [6,7,9,10,11,12,13,15]#,11,12] #,12

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
    
    poolReduced = dimReduce(df_clust_pool)
    np.save(fid_poolRed,poolReduced)
    df_pool.to_pickle(fid_totalPool)
else:
    poolReduced = np.load(fid_poolRed+".npy")
    df_pool =pd.read_pickle(fid_totalPool) 

## Clustering.
#sc = SpectralClustering(n_clusters = nPlaylists,n_jobs=-1)
sc = AgglomerativeClustering(n_clusters = nPlaylists)
# sc = DBSCAN(n_jobs=-1)

splitVals = sc.fit_predict(poolReduced)
nPlaylistOut = np.unique(splitVals).size

for ind in range(0,nPlaylistOut):
    idxTest = np.where(splitVals==ind)
    idxTest = idxTest[0]
    playlistOut = df_pool.iloc[idxTest]
    playName = "".join(("playlist",str(ind),".csv"))
    if ind < nPlayExport and writePlaylists:
        createPlaylist(playName,playlistOut)
    playlistOut.to_csv("/".join((csv_folder_out,playName)))

### TODO: write cluster values back out to some usable variable so I can mess with visualization.
plotly.offline.plot({
"data": [
    plotly.graph_objs.Scatter(    x=poolReduced[:,0],
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
