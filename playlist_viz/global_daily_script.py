import numpy as np 
import pandas as pd
import datetime
import random 
from math import floor

import utils 
from crate_compile import crateCompile
from song_corpus_analysis import analyseSongCorpus
from spotify_interactions import createPlaylist,initSpotipy
import spotify_interactions as si 
#Obviously since everything is written out it's not optimal.
FLAG_RUN = True

runCrateCompile = False
runPlSample = False#True
runTempoRecs = True

if FLAG_RUN:

    ###### sample big playlists
    if runPlSample:
        today=datetime.date.today() 
        recentGenDW = today-datetime.timedelta(days=today.weekday())
        dwDate = recentGenDW.strftime("%m/%d/%Y")
        edgeDate = "07/30/2021"
        pulseDate = "07/15/2021"
        # playlists=["RR Listen through"]
        playlists=[\
                    "downselect_downselect_listen", \
                    "Combined Edge Playlists "+edgeDate, \
                    "Combined Pulse Playlists "+pulseDate,
                    "Combined DW for the Week of "+dwDate, \
                    "RR Listen through"
                    ]
        nPlaylists =2
        nSongsPerPlaylist = 15

        sp = si.initSpotipy("playlist-read-private playlist-modify-private user-library-read")# 
        for elt in playlists:
            si.samplePlaylists(sp,elt,nPlaylists,nSongsPerPlaylist)

    ###### compile crate playlists and sample that.
    if runCrateCompile:
        nExport_crate = 3
        nExport_downsel = 2
        #nExport_archive = 1
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
        analyseSongCorpus(rangeClusterSearch=[200,300],poolSize=10e3,showPlot=False,fid_in=fid_arch,out_append="arch_")


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

        ## run for archive
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
    ######
    if runTempoRecs:
        plSearch="The Downselect, 2021"#"The Downselect, July 2021 Week 3"#"The Downselect"

        targetSampleSize = 50 #20
        tempoDelta = 10
        keyDelta = 3#6
        popRange = [0, 100]
        
        sp = si.initSpotipy("playlist-read-private playlist-modify-private")# 

        pl_id = si.getPlaylistID(sp,plSearch)
        trackDict,analysisDict = si.getTracksFromPlaylist(sp,pl_id,True,True)
        trackDF  = si.tracksToDF(trackDict,analysisDict)
        df_single = trackDF.sample(n=1)
        tempoRange = [-tempoDelta/2+ np.float64(df_single["Tempo"]), np.float64(tempoDelta/2+ df_single["Tempo"])] 
        ### TODO: this is probably still using spotify's keys and not the traktor key format. fix this.
#        df_single = si.djMapKey(df_single)
        key_dj = int(df_single["DJ Key"])
        keyRange = [0+ key_dj ,keyDelta+key_dj]   ### NOTE: this doesn't account for edce case of key < 
        keyDiff = 12 - (keyDelta+key_dj)
        if keyDiff < 0:
            keyRange = [11-keyDelta+1,12]
        seedDF = si.djSort(trackDF,tempoRange,keyRange)

        # draw from the songs in the external playlist 
        nRec = 0
        recsDF = pd.DataFrame() # include seed at top.
        iterCnt = 0
        while nRec < targetSampleSize and iterCnt < 50:
            seedCnt = min(len(seedDF),5)
            seedSamp = seedDF.sample(n=seedCnt)
            seedRec = list(seedSamp["Track ID"])
            recRet = sp.recommendations(seed_tracks=seedRec,limit=targetSampleSize,min_tempo=tempoRange[0],max_tempo = tempoRange[1],market="US",min_popularity=popRange[0],max_popularity=popRange[1])

            tracksRet = recRet["tracks"]
            recIDs_tmp =  [elt["id"] for elt in recRet["tracks"]]
            afRet = sp.audio_features(recIDs_tmp)
            currDF = si.tracksToDF(tracksRet,afRet)

#            currDF = si.djMapKey(currDF)
            currDF = currDF.loc[(currDF["DJ Key"]>= keyRange[0]) & (currDF["DJ Key"] <= keyRange[1])]
            recsDF = recsDF.append(currDF)
            recsDF= recsDF.drop_duplicates(subset=['Track ID'])
            nRec = recsDF.shape[0]
            iterCnt += 1

        recsDF = si.djSort(recsDF,tempoRange,keyRange)
        si.createPlaylist(sp,"DJ Pull "+plSearch,recsDF,incAnalysis = False)

        #trackTempos = [item["tempo"] for item in trackDict if item["id"]]
        #print (trackTempos)
#        tracksIDs = random.shuffle(trackIDs)

        # if genSameSize:
        #     nQuery = floor(len(trackIDs)/targetSampleSize)
        # else:
        #     nQuery = floor(len(trackIDs)/5)

        # for idx in range(nQuery):
        #     if usePopRange:
        #         recRet = sp.recommendations(seed_tracks=trackIDs[idx*5:(idx+1)*5],limit=targetSampleSize,min_tempo=tempoRange[0],max_tempo = tempoRange[1],market="US",min_popularity=popRange[0],max_popularity=popRange[1])
        #     else:
        #         recRet = sp.recommendations(seed_tracks=trackIDs[idx*5:(idx+1)*5],limit=targetSampleSize,min_tempo=tempoRange[0],max_tempo = tempoRange[1],market="US",target_popularity=targetPopularity)
        #     recTracks= recRet["tracks"]
        #     recIDs = recIDs + [elt["id"] for elt in recTracks if ("US" in elt["available_markets"])]

        # # print(recIDs)

        # si.createPlaylist(sp,"Similar to "+plSearch,recIDsUnique,incAnalysis = False)