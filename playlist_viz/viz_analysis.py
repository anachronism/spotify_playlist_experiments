# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 18:46:12 2021

@author: Max
"""

from sklearn.cluster import SpectralClustering
from  sklearn.manifold import TSNE

import numpy as np
import pandas as pd
import seaborn as sns

csv_folder = "playlist_csvs"
csv_folder_out = "output_playlists"

### TODO: add script to run through all csvs in folder.
test_pool =  "_crate_10_.csv" #"liked.csv"
test_ex = "jul_2020_chance_encounters.csv"
nPlaylists = 6

fid_pool = "/".join((csv_folder,test_pool))
fid_ex = "/".join((csv_folder,test_ex))

df_pool = pd.read_csv(fid_pool)
df_pool = df_pool.sample(frac=1)
df_ex = pd.read_csv(fid_ex)

featuresPull = ['Danceability','Energy','Speechiness','Acousticness'
                ,'Instrumentalness','Liveness','Valence','Loudness','Tempo'] # ,'Key'

df_clust_pool = df_pool[featuresPull]
df_clust_ex = df_ex[featuresPull]

np_clust_pool = df_clust_pool.to_numpy()
cleaningInds = np.where(np.isnan(np_clust_pool))
uniqueInds = np.unique(cleaningInds[0])
np_clust_pool = np.delete(np_clust_pool,(uniqueInds),axis=0)

#df_cluster.head()
labels = df_clust_pool.columns.values
toCluster = df_clust_pool.to_numpy()
print(labels)

## EDA Plotting
#g = sns.PairGrid(df_clust_pool)
#g.map(sns.scatterplot)
#
#g2 = sns.PairGrid(df_clust_ex)
#g2.map(sns.scatterplot)

## Dimensionality reduction.
dimRedModel = TSNE()
poolReduced = dimRedModel.fit_transform(np_clust_pool)

## Clustering.
sc = SpectralClustering(n_clusters = nPlaylists,n_jobs=-1)
splitVals = sc.fit_predict(poolReduced)


for ind in range(0,nPlaylists):
    idxTest = np.where(splitVals==ind)
    idxTest = idxTest[0]
    playlistOut = df_pool.iloc[idxTest]
    playName = "".join(("playlist",str(ind),".csv"))
    playlistOut.to_csv("/".join((csv_folder_out,playName)))

sns.scatterplot(poolReduced[:,0],poolReduced[:,1],hue=splitVals)




'''
Danceability
energy
Loudness
speachiness
acousticness
instrumentalness
liveness
valence
tempo (?)
'''
#df_whole.head()

