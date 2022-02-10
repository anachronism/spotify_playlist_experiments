from song_corpus_analysis import analyseSongCorpus
import numpy as np
import pandas as pd
from spotify_interactions import createPlaylist,initSpotipy
import utils

model_folder = "pkl_vals"
fid_big = "/".join((model_folder,"crates_compiled.pkl"))

analyseSongCorpus(rangeClusterSearch=[1500,1550],poolSize=10e3,showPlot=False,fid_in=fid_big,out_append="crate_tmp_")

fid_clustering_thresh = "/".join((model_folder,"crate_tmp_clusters_thresh.pkl"))
fid_clustering = "/".join((model_folder,"crate_tmp_clusters.pkl"))
fid_clusterNum = "/".join((model_folder,"crate_tmp_nPlaylists"))

nExport_crate = 5
df_clustered= pd.read_pickle(fid_clustering)
nPlaylists = np.load(fid_clusterNum+".npy")

df_clustered_thresh = pd.read_pickle(fid_clustering_thresh)
df_centers = df_clustered_thresh.groupby(['Cluster']).mean()
indsPlaylistsOut = utils.drawClusters(df_centers,nExport_crate)
sp = initSpotipy("playlist-read-private playlist-modify-private user-library-read playlist-modify-public ugc-image-upload")#

for ind in indsPlaylistsOut:
    writeOut = df_clustered[df_clustered["Cluster"] == ind]
    createPlaylist(sp,"CRATE Cluster "+str(ind),writeOut,True)
