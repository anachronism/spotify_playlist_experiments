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
from model_fcns import dimReduce,dimReduce_test,runClustering
import utils
import logging

import numpy as np
import pandas as pd
import seaborn as sns

def analyseSongCorpus(rangeClusterSearch=[3600,3650],showPlot=False,poolSize=30e3,projectDown=True,clusterData=True,chooseClusterNum=True,fid_in="pkl_vals/crates_compiled.pkl",out_append=""):


    csv_folder = "playlist_csvs"
    csv_folder_out = "output_playlists"
    model_folder = "pkl_vals"

    fid_poolRed = "/".join((model_folder,out_append+"poolReduced"))
    fid_clustering = "/".join((model_folder,out_append+"clusters.pkl"))
    fid_clusterNum = "/".join((model_folder,out_append+"nPlaylists"))
    fid_totalPool =  "/".join((model_folder,out_append+"totalPool.pkl"))
    fid_clusters_use = "/".join((model_folder,out_append+"clusters_thresh.pkl"))

    ### TODO: add script to run through all csvs in folder.
    #test_ex = "jul_2020_chance_encounters.csv"
    rangePrint = 5
    nPlayExport = 5
    minPlSize = 7 # minimum playlist size.
    ## The "production" set of features.
    # featuresPull = ['Danceability','Energy','Speechiness','Acousticness'
    #                     ,'Instrumentalness','Liveness','Valence','Loudness','Tempo','DJ Key'] #'Key',,'Loudness','Tempo' ### TODO: scale
    featuresPull = ['Danceability','Energy','Speechiness','Acousticness'
                        ,'Instrumentalness','Liveness','Valence','Loudness','Tempo','DJ Key','TimeSig','Loudness'] #'Key',,'Loudness','Tempo' ### TODO: scale loudness, tempo to uniform.
        # Running index, probably inefficient.
    nTrip = 0
    songLenMin = 30 # min length of song to be considered, in seconds
    # Draw randomly from the total pool before doing any processing. Given size of pool, probably the best way to deal with it.
    # fracPool = 0.5 # fraction of songs in pool to sample. 0 to 1.


    ###### APPLY DIM REDUCTION
    if projectDown:
        # Read saved pickle file from crate_compile script.
        df_pool = pd.read_pickle(fid_in)
        print(df_pool.shape)

        # Apply preprocessing.
        df_pool = df_pool[df_pool["Duration_ms"] > songLenMin*1e3]
        print(df_pool.columns)
        poolLen = len(df_pool.index)
        if poolSize > poolLen:
            fracPool = 1
        else:
            fracPool = poolSize/poolLen
        df_pool = df_pool.sample(frac=fracPool)
        df_clust_pool = df_pool[featuresPull]
        df_clust_pool = df_clust_pool.dropna(axis='rows')
        print(df_clust_pool.shape)
        poolReduced = dimReduce(df_clust_pool,3)
        # poolReduced = dimReduce_test(df_clust_pool,3) ##########Note! this needs to be returned.
        fid_poolRed = fid_poolRed+"_3d"

        df_pool["x"] = poolReduced[:,0]
        df_pool["y"] = poolReduced[:,1]
        df_pool["z"] = poolReduced[:,2]

        np.save(fid_poolRed,poolReduced)
        df_pool.to_pickle(fid_totalPool)
        logging.info("CORPUS: dimensionality reduced.")
    else:
        fid_poolRed = fid_poolRed+"_3d"
        poolReduced = np.load(fid_poolRed+".npy")
        df_pool = pd.read_pickle(fid_totalPool)

    ###### APPLY CLUSTERING
    if clusterData:
        ## Clustering.
        if chooseClusterNum:
            df_clustered,nPlaylists = runClustering(df_pool,rangeClusterSearch,True,showPlot)
        else:
            nPlaylists = np.load(fid_clusterNum+".npy")
            df_clustered,nPlaylists = runClustering(df_pool,nPlaylists,False,showPlot)

        logging.info("CORPUS: clustered.")
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
    utils.getExtrema(df_clustersUse,minMaxPlots,rangePrint)

    # minPlots = dict()
    # maxPlots = dict()
    # df_centers_downsel = df_clustersUse.groupby(['Cluster']).mean()

    # for cat in minMaxPlots:
    #     df_sort = df_centers_downsel.sort_values(by=[cat],ascending = True)
    #     minPlots[cat] = df_sort.iloc[0]
    #     maxPlots[cat] = df_sort.iloc[-1]
    #     #print(df_sort.index)
    #     clustersUseValues = clustersUse.index.values
    #     minVals = df_sort.index[0:rangePrint].values
    #     maxVals = np.flip(df_sort.index[-rangePrint:].values)
    #     minStr = str(minVals)
    #     maxStr = str(maxVals)
    #     print("Min "+ cat + ": "+ minStr)
    #     #print(df_sort[cat].iloc[idxValsMin].values)
    #     print("Max "+ cat + ": "+ maxStr)
