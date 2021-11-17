import numpy as np
import pandas as pd
import utils
from crate_compile import crateCompile
from song_corpus_analysis import analyseSongCorpus
import spotify_interactions as si
from math import ceil,floor
import random
import datetime

today=datetime.date.today()

model_folder = "pkl_vals"
playlist_folder = "playlist_csvs"
fid_edge = "/".join((model_folder,"edge_compiled.pkl"))
fid_pulse = "/".join((model_folder,"pulse_compiled.pkl"))
fid_dw = "/".join((model_folder,"dw_compiled.pkl"))

sp = si.initSpotipy("playlist-read-private playlist-modify-private user-library-read")#
mode = "newPulseCluster"#"initEdgePulse"


if mode=="initEdgePulse":
        plCompile_edge = "Combined Edge Playlists"
        plCompile_pulse = "Combined Pulse Playlists"
        si.saveTracksFromPlaylist(sp,plCompile_pulse,fid_pulse)
        print("Pulse compiled!")
        si.saveTracksFromPlaylist(sp,plCompile_edge,fid_edge)
        print("Edge compiled!")

elif mode == "newEdgeCluster":
    RECOMP_EDGE = False
    nExport_edge = 1
    #Compile crates weekly

    if RECOMP_EDGE:
        dateEarly=today-datetime.timedelta(days=7)
        dateLate = today
        dateIn = [dateEarly,dateLate]

        nTracks = si.getNewTracks_df(sp, fid_edge,"The Edge of",dateIn)
        print("Number of tracks in pool: " + str(nTracks))
        # si.crateCompile(sp,fid_in = fid_edge,searchIDs=["The Edge of"])
        # analyseSongCorpus(rangeClusterSearch=[0+int(np.floor(nTracks/30)),100+int(np.floor(nTracks/30))],poolSize=10e3,showPlot=False,fid_in=fid_edge,out_append="edge_")

    si.clusterSinglePlaylist(sp,model_folder,fid_edge,"Combined Edge Playlists",1,analyzeCorpus=RECOMP_EDGE,out_append="edge", pklIn=True)

elif mode == "newPulseCluster":
    RECOMP_PULSE = True
    nExport_pulse = 1
    #Compile crates weekly

    if RECOMP_PULSE:
        dateEarly=today-datetime.timedelta(days=7)
        dateLate = today
        dateIn = [dateEarly,dateLate]

        nTracks = si.getNewTracks_df(sp, fid_pulse,"The Pulse of",dateIn)
        print("Number of tracks in pool: " + str(nTracks))
        # si.crateCompile(sp,fid_in = fid_edge,searchIDs=["The Edge of"])
        # analyseSongCorpus(rangeClusterSearch=[0+int(np.floor(nTracks/30)),100+int(np.floor(nTracks/30))],poolSize=10e3,showPlot=False,fid_in=fid_edge,out_append="edge_")

    si.clusterSinglePlaylist(sp,model_folder,fid_pulse,"Combined Pulse Playlists",1,analyzeCorpus=RECOMP_PULSE,out_append="pulse", pklIn=True)

elif mode == "pulseCluster":
    calcClusters= False
    model_folder = "pkl_vals"

    fid_pulse = "/".join((model_folder,"pulse_compiled.pkl"))
    si.clusterSinglePlaylist(sp,model_folder,fid_pulse,"Combined Pulse Playlists",2,analyzeCorpus=calcClusters)

elif mode == "refreshEdgePulse":
    today = datetime.date.today()
    dateEarly=today-datetime.timedelta(days=7)
    dateLate = today
    dateIn = [dateEarly,dateLate]
    si.getNewTracks(sp,"The Edge of","Combined Edge Playlists",dateIn)
    si.getNewTracks(sp,"The Pulse of","Combined Pulse Playlists",dateIn)
elif mode == "recDrawPlaylist":
    today = datetime.date.today()
    djDate = today.strftime("%m/%d/%Y")

    plSearch="wip | mode2"#"The Downselect, July 2021 Week 3"#"The Downselect"

    targetSampleSize = 100 #20
    ITER_MAX = 100
    tempoDelta = 10
    keyDelta = 3#6
    popRange = [0, 100]

    plName = "DJ Pull "+ djDate+" " + plSearch
    si.getDJrecs(sp,plSearch,plName,targetSampleSize,tempoDelta,keyDelta,popRange,ITER_MAX)
elif mode == "updateEdge":
    dateEarly=today-datetime.timedelta(days=6)
    dateLate = today
    dateIn = [dateEarly,dateLate]
    si.getNewTracks(sp,"The Edge of","Combined Edge Playlists",dateIn)
    # si.getNewTracks(sp,"The Pulse of","lol",dateIn)
elif mode == "updatePulse":
    dateEarly=today-datetime.timedelta(days=6)
    dateLate = today
    dateIn = [dateEarly,dateLate]
    si.getNewTracks(sp,"The Pulse of","Combined Pulse Playlists",dateIn)
    # si.getNewTracks(sp,"The Pulse of","lol",dateIn)
elif mode == "recDateUpdate":

    # createNewPl = (today.day == 1)
    # idsAdjust = si.cyclePlaylist(sp,"The Downselect",nDaysCycle = 7,removeTracks=True,newPl= createNewPl)
    # if idsAdjust:
    #    si.addToPlaylist(sp,"downselect_downselect_listen",idsAdjust)
    now = datetime.datetime.now()
    dtString=now.strftime("%m/%d/%Y")

    playlistTitle = "Combined RR for the Week of " + dtString
    playlistSearch = "Release Radar"
    playlistRemove = "Discovery Avoid"
    si.compilePlaylists(sp,playlistSearch,playlistRemove,playlistTitle)
            ### TODO: Update this to also update the edge playlists with new additions.


elif mode == "djRadioTest":
    today = datetime.date.today()
    djDate = today.strftime("%m/%d/%Y")

    plSearch="wip | mode2"#"The Downselect, July 2021 Week 3"#"The Downselect"

    targetSampleSize = 100 #20
    tempoDelta = 5
    keyDelta = 3#6
    popRange = [0, 100]

    sp = si.initSpotipy("playlist-read-private playlist-modify-private")#

    pl_id = si.getPlaylistID(sp,plSearch)
    trackDict,analysisDict = si.getTracksFromPlaylist(sp,pl_id,True,True)
    trackDF  = si.tracksToDF(trackDict,analysisDict)
    df_single = trackDF.sample(n=1)
    tempoRange = [78, 85]
    key_dj = int(df_single["DJ Key"])
    keyRange = [key_dj ,keyDelta+key_dj]   ### NOTE: this doesn't account for edce case of key <
    keyDiff = 12 - (keyDelta+key_dj)
    if keyDiff < 0:
        keyRange = [12-keyDelta,12]
#        seedDF = si.djSort(trackDF,tempoRange,keyRange)
    seedDF = si.djSort(trackDF,tempoRange,keyRange)

elif mode == "recsQuery":
    ''' This set of code useful for testing the recommendation section'''
    # There's a lot of things that this can be used for (can limit tempo, key etc in rec search and use artists as target)
    #This will become a function when I decide what I want to do with it
    # Can also seed with artists and genres. Max of 5 seeds total.
    plSearch="traffic_soundbwoy_radio"#"The Downselect, July 2021 Week 3"#"The Downselect"
    targetSampleSize = 100#5*2  #20
    pl_id = si.getPlaylistID(sp,plSearch)
    trackDict,analysisDict = si.getTracksFromPlaylist(sp,pl_id,True,True)
    trackDF  = si.tracksToDF(trackDict,analysisDict)
    tempoRange = [78, 85]
    trackIDs  =  [item["id"] for item in trackDict if item["id"]]
    popRange = [0,60]
    recIDs = []
    recIDsUnique = [0]
    iterCount = 0
    N_REP = 100
    while len(recIDsUnique) < targetSampleSize and iterCount < N_REP:
        iterCount += 1
        recRet = sp.recommendations(seed_tracks=trackIDs[0:5],limit=targetSampleSize,min_tempo=tempoRange[0],max_tempo = tempoRange[1],market="US",min_popularity=popRange[0],max_popularity=popRange[1])
        recTracks= recRet["tracks"]
        recIDs = recIDs + [elt["id"] for elt in recTracks if ("US" in elt["available_markets"])]
        recIDsUnique = list(dict.fromkeys(recIDs))
        if len(recIDsUnique)> targetSampleSize:
            break
        print(str(iterCount) + " : " + str(len(recIDsUnique)))
    ### TODO: get recTracks into recIDsUnique format, get sp.audio_features() of the ids to djsort similar playlists.
    si.createPlaylist(sp,"Similar to "+plSearch,recIDsUnique,incAnalysis = False)
