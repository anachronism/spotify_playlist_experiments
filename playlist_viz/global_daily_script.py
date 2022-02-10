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
import logging,os
#Obviously since everything is written out it's not optimal.
today=datetime.date.today()

FLAG_RUN = True
ITER_MAX = 100

model_folder = "pkl_vals"
playlist_folder = "playlist_csvs"

runBools_sample = np.zeros((5,))
runBools_sample[2] = 1

runBools_compile = np.zeros((5,))
runBools_compile[0] = 1

runBools_cycle = np.zeros((5,))

runBools_cycle[1] = 1

### TODO: check how keys are mapped.
runBools_rotate_tempo = np.zeros((5,))
runBools_rotate_tempo[0] = 1
runBools_rotate_tempo[1] = 1
runBools_rotate_tempo[3] = 1

runBools_all = np.ones((5,))
runBools_none = np.zeros((5,))
# runBools = runBools_sample
runBools = runBools_all
# runBools = runBools_compile

#downsel, rr, dw, edge, pulse, sounds
plGenIdx = [0,1,2,3,4,5,6,7]
#plGenIdx = [0,3,4,5,6,7]

runCompileFcns = runBools[0]
runDownselCycle = runBools[1]
runPlSample = runBools[2]
runTempoRecs = runBools[3]
runCrateCompile = False#runBools[4]
runPlArchive = (today.day == 2)

now = datetime.datetime.now()
dtString=now.strftime("%m/%d/%Y")

retVal = 0

logging.basicConfig(filename='globalScript.log',encoding='utf-8',level=logging.INFO) # debug will give me the spotipy debug too lol.
logging.info("Global script run " + dtString)

if FLAG_RUN:
    sp = si.initSpotipy("playlist-read-private playlist-modify-private user-library-read playlist-modify-public ugc-image-upload")#

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

            elif today.weekday() == 4: #
                #Friday, compile release radar playlists.
                playlistTitle = "Combined RR for the Week of " + dtString
                playlistSearch = "Release Radar"
                playlistRemove = "Discovery Avoid"
                si.compilePlaylists(sp,playlistSearch,playlistRemove,playlistTitle)
                logging.info("Compiled RR.")

                fid_edge = "/".join((model_folder,"edge_compiled.pkl"))
                fid_pulse = "/".join((model_folder,"pulse_compiled.pkl"))
                fid_manual = "/".join((model_folder,"sounds_manual_compiled.pkl"))
                fid_sounds = "/".join((model_folder,"sounds_compiled.pkl"))

                fid_crate = "/".join((model_folder,"crates_compiled.pkl"))

                dateEarly=today-datetime.timedelta(days=7)
                dateLate = today
                dateIn = [dateEarly,dateLate]
                nTracks = si.getNewTracks_df(sp, fid_edge,"The Edge of",dateIn)
                logging.info("Compiled Edge Of playlists.")
                nTracks = si.getNewTracks_df(sp, fid_pulse,"The Pulse of",dateIn)
                logging.info("Compiled Pulse Of playlists.")
                nTracks = si.getNewTracks_df(sp, fid_sounds,"The Sound of",dateIn)
                logging.info("Compiled Sound Of playlists.")
                nTracks = si.getNewTracks_df(sp, fid_manual,"CRATE ADD",dateIn)
                logging.info("Compiled Crate playlist.")




                si.dedupDF(fid_sounds)
                # si.removeSavedTracks_df(sp,fid_sounds)
                si.pickle2csv(fid_sounds,"playlist_csvs/sounds_compiled.csv")
                si.dedupDF(fid_edge)
                si.pickle2csv(fid_edge,"playlist_csvs/edge_compiled.csv")
                si.dedupDF(fid_pulse)
                si.pickle2csv(fid_pulse,"playlist_csvs/pulse_compiled.csv")
                si.dedupDF(fid_crate)
                si.pickle2csv(fid_crate,"playlist_csvs/crates_compiled.csv")
                si.dedupDF(fid_manual)
                si.pickle2csv(fid_manual,"playlist_csvs/manual_compiled.csv")


        except Exception as e:
            logging.error(e)
            logging.error("Compilation failed.")
            retVal += 1
    # Move old elements of the downselect playlist into a monthly playlist.
    if runDownselCycle == True:
        try:
            createNewPl = (today.day == 1)
            daysCycle = 7
            idsAdjust = si.cyclePlaylist(sp,"The Downselect",nDaysCycle = daysCycle,removeTracks=True,newPl= createNewPl) ### TODO: return to True.
            # print(idsAdjust)
            if idsAdjust:
               fid_crate = "/".join((model_folder,"crates_compiled.pkl"))
               df_ret = si.addAlbumsToCrate(sp,idsAdjust,fid_crate)
               si.saveTrackDF(df_ret,"playlist_csvs/crates_compiled.csv")
               si.addToPlaylist(sp,"downselect_downselect_listen",idsAdjust)
               print("added!")

        except Exception as e:
            logging.error(e)
            logging.error("Downselect cycle out failed")
            retVal += 2


    ###### sample big playlists
    if runPlSample:
        try:
            today=datetime.date.today()
            recentGenDW = today-datetime.timedelta(days=today.weekday())
            if(today.weekday() < 4):
                recentGenRR = today-datetime.timedelta(days=today.weekday())-datetime.timedelta(days=3)
            else:
                recentGenRR = today-datetime.timedelta(days=today.weekday()) + datetime.timedelta(days=4)
            dwDate = recentGenDW.strftime("%m/%d/%Y")
            rrDate = recentGenRR.strftime("%m/%d/%Y")
            # playlists=["Combined RR for the Week of " + rrDate]
            playlists=[\
                        "downselect_downselect_listen", \
                        "Combined RR for the Week of " + rrDate,\
                        "Combined DW for the Week of "+dwDate \
                        ]

            playlistShort = ["down","rr","dw","edge","pulse","sounds","crate","manual"]

            model_folder = "pkl_vals"
            pkl_locs = [
                "edge_compiled.pkl",\
                "pulse_compiled.pkl", \
                "sounds_compiled.pkl", \
                "crates_compiled.pkl", \
                "sounds_manual_compiled.pkl"
            ]
            nPlaylists =1
            nPlaylists_cluster = 2
            nSongsPerPlaylist = 30
        #    print(playlists)
            if today.weekday() == 0:
                calcClusters = True
            else:
                calcClusters = False

            # calcClusters = True
#
            for idx in plGenIdx:
                print(idx)
                if idx < 3:
                    elt = playlists[idx]
                    plOut = playlistShort[idx]
    #                calcClusters= False
                    model_folder = "pkl_vals"
                    print(elt)
                    fid_pulse = "/".join((model_folder,playlistShort[idx]+"_compiled.pkl"))
                    if idx < 1:
                        for idx2 in range(nPlaylists_cluster):
                            si.clusterSinglePlaylist(sp,model_folder,fid_pulse,elt,nPlaylists,analyzeCorpus=calcClusters,out_append=plOut)
                    else:
                        si.samplePlaylists(sp,elt,nPlaylists,nSongsPerPlaylist)
                else:
                    fid_in ="/".join((model_folder,pkl_locs[idx-3]))
                    plOut = playlistShort[idx]
    #                calcClusters= False
                    for idx3 in range(nPlaylists_cluster):
                        if idx3 == 0:
                            calcClusters_sub = calcClusters
                        else:
                            calcClusters_sub = False
                        si.clusterSinglePlaylist(sp,model_folder,fid_in,False,nPlaylists,analyzeCorpus=calcClusters_sub,out_append=plOut, pklIn=True)

            #df sampled ones.

        except Exception as e:
            logging.error(e)
            logging.error("Playlist subsample failed.")
            retVal += 4


        ######
    if runTempoRecs:
        try:
            today = datetime.date.today()
            djDate = today.strftime("%m/%d/%Y")

            plSearch="The Downselect, 2022"#"The Downselect, July 2021 Week 3"#"The Downselect"

            targetSampleSize = 50 #20
            tempoDelta = 10
            keyDelta = 3#6
            popRange = [0, 100]

            plName = "DJ Pull "+ djDate+" " + plSearch
            si.getDJrecs(sp,plSearch,plName,targetSampleSize,tempoDelta,keyDelta,popRange,ITER_MAX)

        except Exception as e:
            print(e)
            print("creation failed!")
            logging.error("Tempo rec playlist gen failed.")
            logging.error(e)
            retVal += 8

    ###### compile crate playlists and sample that.
    if runCrateCompile:
        try:
            nExport_crate = 1
            nExport_downsel = 1
            nExport_archive = 1
            #bigSearch = ["/* ","The Downselect","/** "]
            model_folder = "pkl_vals"
            fid_big = "/".join((model_folder,"crates_compiled.pkl"))
            fid_small = "/".join((model_folder,"downsel_compiled.pkl"))
            fid_arch = "/".join((model_folder,"archive_compiled.pkl"))

            #Compile crates weekly
            if today.weekday() == 1:
                si.crateCompile(sp,fid_in = fid_big,searchIDs=["/* "])
                si.crateCompile(sp,fid_in = fid_small,searchIDs=["The Downselect"])
                si.crateCompile(sp,fid_in = fid_arch,searchIDs=["/**"])

                analyseSongCorpus(rangeClusterSearch=[3500,3550],poolSize=20e3,showPlot=False,fid_in=fid_big,out_append="crate_")
                analyseSongCorpus(rangeClusterSearch=[900,1000],poolSize=5e3,showPlot=False,fid_in=fid_small,out_append="downsel_")
                analyseSongCorpus(rangeClusterSearch=[2000,2050],poolSize=10e3,showPlot=False,fid_in=fid_arch,out_append="arch_")

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

        except Exception as e:
            logging.error(e)
            logging.error("Clustering subsample failed.")
            retVal += 16

    if runPlArchive:
        try:
            now = datetime.datetime.now()
            dtString=now.strftime("%m-%Y")
            archiveFolder = "playlist_csvs/archive_"+dtString
            if not os.path.exists(archiveFolder):
                os.mkdir(archiveFolder)
            archiveFolder = "playlist_csvs/archive_"+dtString+"/"
            si.saveUserPlaylistsToCSV(sp,archiveFolder)
            # searchStrings = ["The Downselect,","Genre Selects"]
            # for plSearch in searchStrings:
            #     si.savePlaylistsToCSV(sp,plSearch,archiveFolder,False)

        except Exception as e:
            logging.error(e)
            logging.error("Playlist Archival failed.")
            retVal += 32

print("Returns: " + str(retVal))
logging.info("TOP | Return: "+ str(retVal))
