# import numpy as np
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
fid_sounds = "/".join((model_folder,"sounds_compiled.pkl"))
fid_manual = "/".join((model_folder,"sounds_manual_compiled.pkl"))
fid_edge = "/".join((model_folder,"edge_compiled.pkl"))
fid_pulse = "/".join((model_folder,"pulse_compiled.pkl"))
fid_dw = "/".join((model_folder,"dw_compiled.pkl"))
fid_crate = "/".join((model_folder,"crates_compiled.pkl"))
fid_down_archive = "/".join((model_folder,"down_arch_compiled.pkl"))



sp = si.initSpotipy("playlist-read-private playlist-modify-private user-library-read")#
print(sp)
mode = "testDownArchCycle"#"modifyEdge"#"initEdgePulse"
if mode == "testDownArchCycle":
    daysCycle = 180
    idsAdjust,df_base = si.cyclePlaylist(sp,"downselect_downselect_listen",nDaysCycle = daysCycle,removeTracks=True,appendDate=False,newPl= False,df_str=fid_down_archive) ### TODO: return to True
    si.saveTrackDF(df_base,"tmp.csv")
if mode == "initDownArch":
    plCompile_manual = "ARCHIVE: downselect_downselect_listen"
    si.saveTracksFromPlaylists(sp,plCompile_manual,fid_down_archive)
    print("DownArch compiled!")
elif mode == "modifyDownArch":
    trackDF = pd.read_pickle(fid_down_archive)
    si.pickle2csv(fid_down_archive,"playlist_csvs/down_arch_compiled.csv")
    idsAdjust = list(trackDF["Track ID"])
    now = datetime.datetime.now()
    dtString = now.strftime("%m/%d/%Y")
    trackDF["Date Added"] = dtString
    si.dedupDF(fid_down_archive)
elif mode == "modifyManualCrates":
    trackDF = pd.read_pickle(fid_manual)
    trackDict,analysisDict = si.compilePlaylists_dicts(sp,"CRATE ADD")
#    print(trackDict[0].keys())
    trackDF2 = si.tracksToDF(trackDict,analysisDict,False)
    trackDF.append(trackDF2)
    idsAdjust = list(trackDF["Track ID"])
    now = datetime.datetime.now()
    dtString = now.strftime("%m/%d/%Y")
    trackDF["Date Added"] = dtString
    si.dedupDF(fid_manual)
    si.pickle2csv(fid_manual,"playlist_csvs/manual_compiled.csv")

    trackDF.to_pickle(fid_manual)
    si.saveTrackDF(trackDF,'manual_compiled.csv')
elif mode == "initManualCrates":
    plCompile_manual = "CRATE ADD ALT"
    si.saveTracksFromPlaylists(sp,plCompile_manual,fid_manual)
    print("Sounds compiled!")

elif mode == "testSample":
    #downsel, rr, dw, edge, pulse, sounds, crates

    calcClusters = True
    plGenIdx = [6]

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

    playlistShort = ["down","rr","dw","edge","pulse","sounds","crate"]

    model_folder = "pkl_vals"
    pkl_locs = [
        "edge_compiled.pkl",\
        "pulse_compiled.pkl", \
        "sounds_compiled.pkl", \
        "crates_compiled.pkl"
    ]
    nPlaylists =1
    nPlaylists_cluster = 2
    nSongsPerPlaylist = 30
    #
#    print(playlists)
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
elif mode == "importCSV":
    csvFolder = "playlist_csvs/playlists_feb2021_archive/"
    csvImport = csvFolder+"the_downselect_december_2020.csv"
    si.csv2playlist(sp,csvImport, "The Downselect, December 2020")

elif mode == "archivePlaylists": #### THIS I still need to test.
    exportFolder = "playlist_csvs/archive/"
    si.saveUserPlaylistsToCSV(sp,exportFolder)

elif mode == "dedupCrates":
    si.dedupDF(fid_sounds)
    # si.removeSavedTracks_df(sp,fid_sounds)
    si.pickle2csv(fid_sounds,"playlist_csvs/sounds_compiled.csv")
    si.dedupDF(fid_edge)
    si.pickle2csv(fid_edge,"playlist_csvs/edge_compiled.csv")
    si.dedupDF(fid_pulse)
    si.pickle2csv(fid_pulse,"playlist_csvs/pulse_compiled.csv")
    si.dedupDF(fid_crate)
    si.pickle2csv(fid_crate,"playlist_csvs/crates_compiled.csv")

elif mode == "getAlbumsFromIds":
    playID = si.getPlaylistID(sp,"DJ Pull 01/22/2022 The Downselect, 2021")
    idsAdjust = si.getTracksFromPlaylist(sp,playID,ret_track_info = False,ret_af = False,ret_pl_info=False)
    df_ret = si.addAlbumsToCrate(sp,idsAdjust,fid_crate)
    si.saveTrackDF(df_ret,"crates_compiled.csv")



elif mode == "modifyEdge":
    trackDF = pd.read_pickle(fid_edge)
    # idsAdjust = list(trackDF["Track ID"])
    # now = datetime.datetime.now()
    # dtString = now.strftime("%m/%d/%Y")
    # trackDF["Date Added"] = dtString
    print(trackDF["Date Added"])
    #trackDF = trackDF[trackDF["DateAdded"]]
    # trackDF.to_pickle(fid_edge)
    # si.saveTrackDF(trackDF,'crates_compiled.csv')

elif mode == "modifySounds":
    trackDF = pd.read_pickle(fid_sounds)
    idsAdjust = list(trackDF["Track ID"])
    now = datetime.datetime.now()
    dtString = now.strftime("%m/%d/%Y")
    trackDF["Date Added"] = dtString
    trackDF.to_pickle(fid_crate)
    si.saveTrackDF(trackDF,'sounds_compiled.csv')
elif mode == "initSounds":
    plCompile_sounds = "The Sound of"
    si.saveTracksFromPlaylists(sp,plCompile_sounds,fid_sounds)
    print("Sounds compiled!")
elif mode=="modifyCrate":
    trackDF = pd.read_pickle(fid_crate)
    idsAdjust = list(trackDF["Track ID"])
    now = datetime.datetime.now()
    dtString = now.strftime("%m/%d/%Y")
    trackDF["Date Added"] = dtString
    trackDF.to_pickle(fid_crate)
    si.saveTrackDF(trackDF,'crates_compiled.csv')
elif mode=="initCrate":
        plCompile_crate = "/*"
        si.saveTracksFromPlaylists(sp,plCompile_crate,fid_crate)
        print("Crates compiled!")

elif mode == "manualSetup":
    # idsAdjust = si.cyclePlaylist(sp,"The Downselect",nDaysCycle = 7,removeTracks=True,newPl= True)
    # if idsAdjust:
    #    si.addToPlaylist(sp,"downselect_downselect_listen",idsAdjust)
    now = datetime.datetime.now()
    dtString=now.strftime("%m/%d/%Y")

    # Monday, create discover weekly.
    # playlistTitle = "Combined DW for the Week of " + dtString
    # playlistSearch = "Discover Weekly"
    # playlistRemove = "Discovery Avoid"
    # si.compilePlaylists(sp,playlistSearch,playlistRemove,playlistTitle)
    playlistTitle = "Combined RR for the Week of " + dtString
    playlistSearch = "Release Radar"
    playlistRemove = "Discovery Avoid"
    si.compilePlaylists(sp,playlistSearch,playlistRemove,playlistTitle)

elif mode == "getGenresDownsel":
    plGet = "The Downselect, 2021"
    playID = si.getPlaylistID(sp,plGet)

    trackDict,analysisDict = si.getTracksFromPlaylist(sp,playID,True,True)
    if analysisDict is None:
        trackDict,analysisDict = si.getTracksFromPlaylist(sp,playID,True,True)

    idxUse = [idx for idx,val in enumerate(analysisDict) if not (val is None)]
    trackDictUse = [trackDict[idx] for idx in idxUse]
    analysisDictUse = [analysisDict[idx]for idx in idxUse]
    trackDF = si.tracksToDF(trackDictUse,analysisDictUse,False)
    (genreVals,genreCount) = si.getTopGenres(sp,trackDF)
    DF_genre = pd.DataFrame({"Genre":genreVals,"GenreCount":genreCount})
    DF_genre.to_csv("end_of_year_genres.csv")

elif mode=="initEdgePulse":
        plCompile_edge = "Combined Edge Playlists"
        plCompile_pulse = "Combined Pulse Playlists"
        plCompile_dw = "Combined DW Playlists "
        si.saveTracksFromPlaylist(sp,plCompile_pulse,fid_pulse)
        print("Pulse compiled!")
        si.saveTracksFromPlaylist(sp,plCompile_edge,fid_edge)
        print("Edge compiled!")
elif mode == "removeEdgeLiked":
    si.saveTrackDF(pd.read_pickle(fid_edge),'pre_removal.csv')
    si.removeSavedTracks_df(sp,fid_edge)
    si.saveTrackDF(pd.read_pickle(fid_edge),'post_removal.csv')
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

    plSearch="Genre Selects: Lofi + beats "#"The Downselect, July 2021 Week 3"#"The Downselect"
    print("here")
    targetSampleSize = 100 #20
    ITER_MAX = 50#100
    tempoDelta = 5
    keyDelta = 3#3#6
    popRange = [0, 60]

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
    plSearch="Genre Selects: Lofi + beats"#"The Downselect, July 2021 Week 3"#"The Downselect"
    targetSampleSize = 100#5*2  #20
    pl_id = si.getPlaylistID(sp,plSearch)
    trackDict,analysisDict = si.getTracksFromPlaylist(sp,pl_id,True,True)
    trackDF  = si.tracksToDF(trackDict,analysisDict)
    tempoRange = [80,87]#[78, 85]
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
else:
    print("Invalid command string.")
