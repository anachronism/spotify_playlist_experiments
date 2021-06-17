import numpy as np 
import pandas as pd
import utils 
from crate_compile import crateCompile
from song_corpus_analysis import analyseSongCorpus
from spotify_interactions import createPlaylist,initSpotipy

#Obviously since everything is written out it's not optimal.
nExport_crate = 3
nExport_downsel = 2
nExport_archive = 1
#bigSearch = ["/* ","The Downselect","/** "]
model_folder = "pkl_vals"
fid_big = "/".join((model_folder,"crates_compiled.pkl"))
fid_small = "/".join((model_folder,"downsel_compiled.pkl"))
fid_arch = "/".join((model_folder,"archive_compiled.pkl"))

#Compile crates
crateCompile(fid_in = fid_big,searchIDs=["/* "])
crateCompile(fid_in = fid_small,searchIDs=["The Downselect"])
crateCompile(fid_in = fid_arch,searchIDs=["/**"])

analyseSongCorpus(rangeClusterSearch=[3500,3550],poolSize=20e3,showPlot=False,fid_in=fid_big,out_append="crate_")
analyseSongCorpus(rangeClusterSearch=[900,1000],poolSize=5e3,showPlot=False,fid_in=fid_small,out_append="downsel_")
analyseSongCorpus(rangeClusterSearch=[2400,2500],poolSize=10e3,showPlot=False,fid_in=fid_arch,out_append="arch_")

# actually draw and such.

sp = initSpotipy("playlist-modify-private")

## run for crates
fid_clustering_thresh = "/".join((model_folder,"crate_clusters_thresh.pkl"))
fid_clustering = "/".join((model_folder,"crate_clusters.pkl"))
fid_clusterNum = "/".join((model_folder,"crate_nPlaylists"))

df_clustered= pd.read_pickle(fid_clustering)
nPlaylists = np.load(fid_clusterNum+".npy")

df_clustered_thresh = pd.read_pickle(fid_clustering_thresh)
df_centers = df_clustered_thresh.groupby(['Cluster']).mean()
indsPlaylistsOut = utils.drawClusters(df_centers,nExport_crate)    


for ind in indsPlaylistsOut:
    writeOut = df_clustered[df_clustered["Cluster"] == ind]
    createPlaylist(sp,"CRATE Cluster "+str(ind),writeOut,True)

## run for downsel
fid_clustering_thresh = "/".join((model_folder,"downsel_clusters_thresh.pkl"))
fid_clustering = "/".join((model_folder,"downsel_clusters.pkl"))
fid_clusterNum = "/".join((model_folder,"downsel_nPlaylists"))

df_clustered= pd.read_pickle(fid_clustering)
nPlaylists = np.load(fid_clusterNum+".npy")

df_clustered_thresh = pd.read_pickle(fid_clustering_thresh)
df_centers = df_clustered_thresh.groupby(['Cluster']).mean()
indsPlaylistsOut = utils.drawClusters(df_centers,nExport_downsel)    


for ind in indsPlaylistsOut:
    writeOut = df_clustered[df_clustered["Cluster"] == ind]
    createPlaylist(sp,"DOWN Cluster "+str(ind),writeOut,True)

## run for downsel
fid_clustering_thresh = "/".join((model_folder,"arch_clusters_thresh.pkl"))
fid_clustering = "/".join((model_folder,"arch_clusters.pkl"))
fid_clusterNum = "/".join((model_folder,"arch_nPlaylists"))

df_clustered= pd.read_pickle(fid_clustering)
nPlaylists = np.load(fid_clusterNum+".npy")

df_clustered_thresh = pd.read_pickle(fid_clustering_thresh)
df_centers = df_clustered_thresh.groupby(['Cluster']).mean()
indsPlaylistsOut = utils.drawClusters(df_centers,nExport_archive)    


for ind in indsPlaylistsOut:
    writeOut = df_clustered[df_clustered["Cluster"] == ind]
    createPlaylist(sp,"ARCHIVE Cluster "+str(ind),writeOut,True)

