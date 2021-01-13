# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 18:46:12 2021

@author: Max
"""

from sklearn.cluster import SpectralClustering,DBSCAN,AgglomerativeClustering
from  sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

import numpy as np
import pandas as pd
import seaborn as sns

csv_folder = "playlist_csvs"
csv_folder_out = "output_playlists"

### TODO: add script to run through all csvs in folder.
test_pool =  "_crate_10_.csv" #"liked.csv" #
test_ex = "jul_2020_chance_encounters.csv"
nPlaylists = 6
crate_range = [10,11]#,11,12] #,12
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
print("HERE1")
## Clustering.
sc = SpectralClustering(n_clusters = nPlaylists,n_jobs=-1)
#sc = AgglomerativeClustering(n_clusters = nPlaylists,n_jobs=-1)
#sc = DBSCAN(n_jobs=-1)
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
sns.scatterplot(poolReduced[:,0],poolReduced[:,1],hue=splitVals)






