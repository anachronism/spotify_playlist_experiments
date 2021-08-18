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
import logging
#Obviously since everything is written out it's not optimal.
today=datetime.date.today() 

FLAG_RUN = True
ITER_MAX = 100

### TODO: check how keys are mapped.
runBools = [1,1,1,1,1]
runCompileFcns = runBools[0]
runDownselCycle = runBools[1]
runCrateCompile = runBools[2]
runPlSample = runBools[3]
runTempoRecs = runBools[4]



now = datetime.datetime.now()
dtString=now.strftime("%m/%d/%Y-")

logging.basicConfig(filename='globalScript.log',encoding='utf-8',level=logging.DEBUG)
logging.info("Global script run " + dtString)

if FLAG_RUN:
    sp = si.initSpotipy("playlist-read-private playlist-modify-private user-library-read")# 


    if runCompileFcns:
        try:        
            now = datetime.datetime.now()
            dtString=now.strftime("%m/%d/%Y")

            if today.weekday() == 0:
                # Monday, create discover weekly.
                playlistTitle = "Combined DW for the Week of " + dtString
                playlistSearch = "Discover Weekly"
                playlistRemove = "Discovery Avoid"
                si.compilePlaylists(sp,playlistSearch,playlistRemove,playlistTitle)

            elif today.weekday() == 4:
                #Friday, compile release radar playlists.
                playlistTitle = "Combined RR for the Week of " + dtString
                playlistSearch = "Release Radar"
                playlistRemove = "Discovery Avoid"
                si.compilePlaylists(sp,playlistSearch,playlistRemove,playlistTitle)
                ### TODO: Update this to also update the edge playlists with new additions.
                ### ToDO: Update this to also update the pulse playlists.
        except: 
            logging.error("Compilation failed.")

    # Move old elements of the downselect playlist into a monthly playlist.    
    if runDownselCycle == True:
        try:
            createNewPl = (today.day == 1)
            idsAdjust = si.cyclePlaylist(sp,"The Downselect",nDaysCycle = 7,removeTracks=True,newPl= createNewPl)
            if idsAdjust:
               si.addToPlaylist(sp,"downselect_downselect_listen",idsAdjust)
        except: 
            logging.error("Downselect cycle out failed") 


    ###### sample big playlists
    if runPlSample:
        try:
            today=datetime.date.today() 
            recentGenDW = today-datetime.timedelta(days=today.weekday())
            recentGenRR = today-datetime.timedelta(days=today.weekday())-datetime.timedelta(days=3)
            dwDate = recentGenDW.strftime("%m/%d/%Y")
            rrDate = recentGenRR.strftime("%m/%d/%Y")

            edgeDate = "07/30/2021"
            pulseDate = "07/15/2021"
            # playlists=["Combined RR for the Week of " + rrDate]
            playlists=[\
                        "downselect_downselect_listen", \
                        "Combined Edge Playlists "+edgeDate, \
                        "Combined Pulse Playlists "+pulseDate,
                        "Combined RR for the Week of " + rrDate,
                        "Combined DW for the Week of "+dwDate \
                        ]
            nPlaylists =2
            nSongsPerPlaylist = 15
            for elt in playlists:
                si.samplePlaylists(sp,elt,nPlaylists,nSongsPerPlaylist)
        except:
            logging.error("Playlist subsample failed.")
            
        ######
    if runTempoRecs:
        try:
            today = datetime.date.today() 
            djDate = today.strftime("%m/%d/%Y")

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
            key_dj = int(df_single["DJ Key"])
            keyRange = [key_dj ,keyDelta+key_dj]   ### NOTE: this doesn't account for edce case of key < 
            keyDiff = 12 - (keyDelta+key_dj)
            if keyDiff < 0:
                keyRange = [12-keyDelta,12]
    #        seedDF = si.djSort(trackDF,tempoRange,keyRange)
            seedDF = si.djSort(trackDF,tempoRange,[1,12])

            # draw from the songs in the external playlist 
            nRec = 0
            recsDF = pd.DataFrame() # include seed at top.
            iterCnt = 0
            ### TODO: decide how much of this should be abstracted into spotify_interactions.
            while nRec < targetSampleSize and iterCnt < ITER_MAX:
                seedCnt = min(len(seedDF),5)
                seedSamp = seedDF.sample(n=seedCnt)

                seedRec = list(seedSamp["Track ID"])
                recRet = sp.recommendations(seed_tracks=seedRec,limit=targetSampleSize,min_tempo=tempoRange[0],max_tempo = tempoRange[1],market="US",min_popularity=popRange[0],max_popularity=popRange[1])

                tracksRet = recRet["tracks"]
                recIDs_tmp =  [elt["id"] for elt in recRet["tracks"]]
                afRet = sp.audio_features(recIDs_tmp)
                currDF = si.tracksToDF(tracksRet,afRet)
                ### TODO: make this work with 
                currDF = currDF.loc[(currDF["DJ Key"]>= keyRange[0]) & (currDF["DJ Key"] < keyRange[1])]
                recsDF = recsDF.append(currDF)
                recsDF= recsDF.drop_duplicates(subset=['Track ID'])
                nRec = recsDF.shape[0]
                iterCnt += 1

            recsDF = si.djSort(recsDF,tempoRange,keyRange)
            print(recsDF)
            # print(recsDF["DJ Key"])
            # print(recsDF["Key"])
            # print(keyRange)
            si.createPlaylist(sp,"DJ Pull "+ djDate+" " + plSearch,recsDF,incAnalysis = False)
        except:
            print("creation failed!")
            logging.error("Tempo rec playlist gen failed.")


    ###### compile crate playlists and sample that.
    if runCrateCompile:
        try:
            nExport_crate = 1
            nExport_downsel = 1
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
        except:
            logging.error("Clustering sample failed.")
