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

from spotify_interactions import createPlaylist,initSpotipy
from model_fcns import dimReduce,runClustering

import numpy as np
import pandas as pd
import seaborn as sns

projectDown = False
clusterData = True
chooseClusterNum = False

csv_folder = "playlist_csvs"
csv_folder_out = "output_playlists"
model_folder = "pkl_vals"

fid_poolRed = "/".join((model_folder,"poolReduced"))
fid_clustering = "/".join((model_folder,"clusters.pkl"))
fid_clusterNum = "/".join((model_folder,"nPlaylists"))
fid_totalPool =  "/".join((model_folder,"totalPool.pkl"))
fid_inputPkl = "/".join((model_folder,"crates_compiled.pkl"))
fid_clusters_use = "/".join((model_folder,"clusters_thresh.pkl"))

### TODO: add script to run through all csvs in folder.
#test_ex = "jul_2020_chance_encounters.csv"
rangeClusterSearch = [3000,3050] #Right now, personal sweet spot is in this range
rangePrint = 5
nPlayExport = 5
minPlSize = 7 # minimum playlist size.
featuresPull = ['Danceability','Energy','Speechiness','Acousticness'
                    ,'Instrumentalness','Liveness','Valence','Loudness','Tempo'] #'Key',,'Loudness','Tempo' ### TODO: scale loudness, tempo to uniform.
    # Running index, probably inefficient.
#playlistMax = dict()
#playlistMin = dict()
nTrip = 0
#maxVals = np.zeros(len(minMaxPlots))
#minVals = np.ones(len(minMaxPlots))


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


### Limit playlist sizes
#tmp = df_clustered.groupby(['Cluster'])
clusterSizes = df_clustered['Cluster'].value_counts()
clustersUse = clusterSizes[clusterSizes>=minPlSize]
#print(clustersUse.shape)
clustersEphemera = clusterSizes[clusterSizes < minPlSize]
df_clustersUse = df_clustered[df_clustered['Cluster'].isin(clustersUse.index.values)]

df_clustersUse.to_pickle(fid_clusters_use)

### NOTE: put epehemera into one cluster/playlist
#df_clustered = df_clustersUse # done this way currently just to evaluate temporarily.


############### Get max and min values.
minMaxPlots = ["Acousticness","Danceability","Valence","Energy"]
minPlots = dict()
maxPlots = dict()
df_centers_downsel = df_clustersUse.groupby(['Cluster']).mean()

for cat in minMaxPlots:
    df_sort = df_centers_downsel.sort_values(by=[cat],ascending = True)
    minPlots[cat] = df_sort.iloc[0]
    maxPlots[cat] = df_sort.iloc[-1]
    #print(df_sort.index)
    clustersUseValues = clustersUse.index.values
    minVals = df_sort.index[0:rangePrint].values
    maxVals = np.flip(df_sort.index[-rangePrint:].values)
    minStr = str(minVals)
    maxStr = str(maxVals)
    print("Min "+ cat + ": "+ minStr)
    #print(df_sort[cat].iloc[idxValsMin].values)
    print("Max "+ cat + ": "+ maxStr)



