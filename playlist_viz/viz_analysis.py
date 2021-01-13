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
from  sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

import numpy as np
import pandas as pd
import seaborn as sns

runFramed = False
projectDown = True

csv_folder = "playlist_csvs"
csv_folder_out = "output_playlists"

### TODO: add script to run through all csvs in folder.
test_pool =  "_crate_10_.csv" #"liked.csv" #
test_ex = "jul_2020_chance_encounters.csv"
nPlaylists = 150#6
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
    scaler = StandardScaler()
    
    df_clust_pool = df_pool[featuresPull]
    df_clust_pool = df_clust_pool.dropna(axis='rows')
    np_clust_pool = scaler.fit_transform(df_clust_pool)
    
    df_clust_ex = df_ex[featuresPull]
    
    #np_clust_pool = df_clust_pool.to_numpy()
    
    #df_cluster.head()
    #Prescale inputs
    
    labels = df_clust_pool.columns.values
    toCluster = df_clust_pool.to_numpy()
    print(labels)
    
    ## EDA Plotting
    #g = sns.PairGrid(df_clust_pool)
    #g.map(sns.scatterplot)
    #
    #g2 = sns.PairGrid(df_clust_ex)
    #g2.map(sns.scatterplot)
    print("HERE0")
    ## Dimensionality reduction.
    dimRedModel = TSNE()
    poolReduced = dimRedModel.fit_transform(np_clust_pool)
    sns.scatterplot(poolReduced[:,0],poolReduced[:,1])

    
## 
if runFramed:
    bl_corner = input("Bottom left corner (x,y):")
    bl_coords = bl_corner.split(",")
    tr_corner = input("Top right corner (x,y):")
    tr_coords = tr_corner.split(",")
    
    ### THIS IS JANK, probably find a better way to do this.
    for ind,elt in enumerate(tr_coords):
        tmp = elt.replace("(",'')
        tr_coords[ind] = np.float64(tmp.replace(")",""))
    for ind,elt in enumerate(bl_coords):
        tmp = elt.replace("(",'')
        bl_coords[ind] = np.float64(tmp.replace(")",""))
    
    #write out specified box
    xrange_limit = np.logical_and((poolReduced[:,0]< tr_coords[0]) , (poolReduced[:,0] > bl_coords[0]))
    yrange_limit = np.logical_and(poolReduced[:,1]< tr_coords[1],poolReduced[:,1] > bl_coords[1])
    specRange = np.where(np.logical_and(xrange_limit,yrange_limit))
    idxSave =  specRange[0]
    playlistOut = df_pool.iloc[idxSave]
    #playName = "".join(("playlist",str(ind),".csv"))
    playlistOut.to_csv("/".join((csv_folder_out,"playlist_spec.csv")))
    #specRange = [specRange_0(0),specRange_1(0)]
else:
        ## Clustering.
    #sc = SpectralClustering(n_clusters = nPlaylists,n_jobs=-1)
    sc = AgglomerativeClustering(n_clusters = nPlaylists)
       # sc = DBSCAN(n_jobs=-1)
    
    splitVals = sc.fit_predict(poolReduced)
    nPlaylistOut = np.unique(splitVals).size
    print("HERE2")
    
    for ind in range(0,nPlaylistOut):
        idxTest = np.where(splitVals==ind)
        idxTest = idxTest[0]
        playlistOut = df_pool.iloc[idxTest]
        playName = "".join(("playlist",str(ind),".csv"))
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
