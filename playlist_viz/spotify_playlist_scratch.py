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

sp = si.initSpotipy("playlist-read-private playlist-modify-private user-library-read")# 
mode = "djRadioTest"

if mode == "recDateUpdate":

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

    plSearch="The Downselect, 2021"#"The Downselect, July 2021 Week 3"#"The Downselect"

    targetSampleSize = 50 #20
    tempoDelta = 10
    keyDelta = 3#6
    popRange = [0, 100]
    
    sp = si.initSpotipy("playlist-read-private playlist-modify-private")# 

    pl_id = si.getPlaylistID(sp,plSearch)
    trackDict,analysisDict = si.getTracksFromPlaylist(sp,pl_id,True,True)
    trackDF  = si.tracksToDF(trackDict,analysisDict)
    print(trackDF["Mode"])
#     df_single = trackDF.sample(n=1)
#     tempoRange = [-tempoDelta/2+ np.float64(df_single["Tempo"]), np.float64(tempoDelta/2+ df_single["Tempo"])] 
#     key_dj = int(df_single["DJ Key"])
#     keyRange = [key_dj ,keyDelta+key_dj]   ### NOTE: this doesn't account for edce case of key < 
#     keyDiff = 12 - (keyDelta+key_dj)
#     if keyDiff < 0:
#         keyRange = [12-keyDelta,12]
# #        seedDF = si.djSort(trackDF,tempoRange,keyRange)
#     seedDF = si.djSort(trackDF,tempoRange,[1,12])

elif mode == "recsQuery":
    ''' This set of code useful for testing the recommendation section'''
    # There's a lot of things that this can be used for (can limit tempo, key etc in rec search and use artists as target)
    #This will become a function when I decide what I want to do with it
    # Can also seed with artists and genres. Max of 5 seeds total.
    plSearch="The Downselect, 2021"#"The Downselect, July 2021 Week 3"#"The Downselect"

    genSameSize = True
    usePopRange = True

    targetSampleSize = 5*2  #20
    recIDs = []
    #tempoRange = [100,105]
    tempoRange = [0, 200]
    targetPopularity = 30#30
    popRange = [0, 60]

    pl_id = si.getPlaylistID(sp,plSearch)
    trackDict,__ = si.getTracksFromPlaylist(sp,pl_id,True,True)
    trackIDs  =  [item["id"] for item in trackDict if item["id"]]
    tracksIDs = random.shuffle(trackIDs)

    if genSameSize:
        nQuery = floor(len(trackIDs)/targetSampleSize)
    else:
        nQuery = floor(len(trackIDs)/5)

    for idx in range(nQuery):
        if usePopRange:
            recRet = sp.recommendations(seed_tracks=trackIDs[idx*5:(idx+1)*5],limit=targetSampleSize,min_tempo=tempoRange[0],max_tempo = tempoRange[1],market="US",min_popularity=popRange[0],max_popularity=popRange[1])
        else:
            recRet = sp.recommendations(seed_tracks=trackIDs[idx*5:(idx+1)*5],limit=targetSampleSize,min_tempo=tempoRange[0],max_tempo = tempoRange[1],market="US",target_popularity=targetPopularity)
        recTracks= recRet["tracks"]
        recIDs = recIDs + [elt["id"] for elt in recTracks if ("US" in elt["available_markets"])]

    # print(recIDs)
    recIDsUnique = list(dict.fromkeys(recIDs))
    si.createPlaylist(sp,"Similar to "+plSearch,recIDsUnique,incAnalysis = False)
