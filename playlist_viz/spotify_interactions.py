# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 19:09:45 2021

@author: Max

"""
# Shows the top tracks for a user

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import secretsLocal ### NOTE: Must create this file yourself. Make functions that return the id and secret.
import pandas as pd 
import numpy as np
from datetime import datetime,date,timedelta

import random 
from math import floor
## Spotipy interactions
# initSpotipy(scope): Initialize the spotipy handle with the scope provided. Note, you must use your own secretsLocal file.
def initSpotipy(scope):
    CLIENT_ID = secretsLocal.clientID()
    CLIENT_SECRET = secretsLocal.clientSecret()
    REDIRECT_URI = "http://localhost:8080" # NOTE:Must add this to your spotify app suitable links. 
        
    return spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,client_id=CLIENT_ID,client_secret=CLIENT_SECRET,redirect_uri=REDIRECT_URI))


'''
Higher level functions
'''
def removeUnplayableSongs(sp,plNames):
    pl_id = getPlaylistID(sp,plName)
    if pl_id == -1:
        print("PLAYLIST NOT FOUND")  
        return -1
    else:  
        tracks_pl,analysis_pl = getTracksFromPlaylist(sp,pl_id,True,True)
        df_pl = tracksToDF(tracks_pl,analysis_pl,False)
        print(df_pl["market"])
        df_remove = df_pl[df_pl["market"].isin(["us"])]                

def searchPlaylistForTempo(sp,plName,bpmRange,checkDouble=True):
    pl_id = getPlaylistID(sp,plName)
    if pl_id == -1:
        print("PLAYLIST NOT FOUND")  
        return -1
    else:  
        tracks_pl,analysis_pl = getTracksFromPlaylist(sp,pl_id,True,True)
        df_pl = tracksToDF(tracks_pl,analysis_pl,False)
        df_out = getTracksWithTempo(df_pl,bpmRange)
        return df_out

'''
Useful things.
'''
## ID acquisitions
# getPlaylistID(sp,strName): With sp handle, get the first playlist that has a title that directly matches the provided string.
def getPlaylistID(sp,strName):    
    # search, must match.
    currUser = sp.me()
    userID = currUser["id"]

    foundPlaylist = False
    offset = 0
   # currVal = sp.current_user_playlists(limit=50, offset=offset)
        
    while not foundPlaylist:
        currVal = sp.current_user_playlists(limit=50, offset=offset)
        plList = currVal["items"]
        tmp = next((item for item in plList if item["name"] == strName),None)
        if not (tmp is None):
            foundPlaylist = True
            return tmp["id"]
        else:
            offset = offset +currVal["limit"]

        if (currVal["next"] is None):
            return -1

# getPlaylistIDs(sp,strName): With sp handle, get all playlist IDs that have titles that have a provided substring.
def getPlaylistIDs(sp,strName):        
    currUser = sp.me()
    userID = currUser["id"]

    idsRet = []
    offset = 0
    currVal = sp.current_user_playlists(limit=50, offset=offset)
    while not (currVal["next"] is None):
        currVal = sp.current_user_playlists(limit=50, offset=offset)
        plList = currVal["items"]

        tmp = [item for item in plList if (strName.lower() in item["name"].lower()) ]  
        for elt in tmp:
            idsRet.append(elt["id"])
            # print(elt["name"])

        offset = offset +currVal["limit"]

    return idsRet

# getTracksFromPlaylist(sp,plID,ret_track_info,ret_af):
# With sp handle and playlist ID, return list with info. if ret_track_info is True, it will return the whole song structure,
# otherwise it returns a list of track IDs. If ret_af is True it also returns the audio-features object for each track.
def getTracksFromPlaylist(sp,plID,ret_track_info = True,ret_af = True, ret_pl_info = False):

    currUser = sp.current_user()
    # print(currUser)
    currMarket="US"#currUser["country"]

    offset = 0
    plHandle = sp.playlist_items(plID,offset = offset,market=currMarket)
    nTracks = plHandle["total"]
    trackIds = []
    #trackURIs = []
    audioFeatures = []
    audioAnalysis = []
    tracksSave = []
    trackDates_save = []
    ret_track_info = ret_track_info
    ret_af = ret_af
    nextUp = 1
    while not (nextUp is None):
        if nextUp != 1:
            offset = offset + plHandle["limit"]
        # save tracks.

        plHandle = sp.playlist_items(plID,offset = offset,market=currMarket) 
        tracksNew = [item["track"] for item in plHandle["items"]]
        trackDates = [item["added_at"] for item in plHandle["items"]]
        tracksSave = tracksSave + tracksNew
        trackDates_save += trackDates 

        tracksNew = list(filter(None,tracksNew))
        newIDs = [item["id"]for item in tracksNew if item["id"]]
        trackIds = trackIds + newIDs

        if ret_af:
            audioFeatures = audioFeatures + sp.audio_features(newIDs)
        nextUp = plHandle["next"]

    if ret_track_info:
        retVals = [tracksSave]
#        trackOut = tracksSave
    else:
        retVals = [trackIds]
#        trackOut = trackIds#trackURIs
    if ret_af:
        retVals += [audioFeatures]
    if ret_pl_info:
        retVals += [trackDates_save]

    return tuple(retVals)


def djMapKey(dfIn):
    dict_keymap_maj = {
        0:1,
        1:8,
        2:3,
        3:10,
        4:5,
        5:12,
        6:7,
        7:2,
        8:9,
        9:4,
        10:11,
        11:6
    }

    dict_keymap_min = {
            0:10,
            1:5,
            2:12,
            3:7,
            4:2,
            5:9,
            6:4,
            7:11,
            8:6,
            9:1,
            10:8,
            11:3
        }    

    df_major = dfIn[dfIn["Mode"] == 1]
    df_minor = dfIn[dfIn["Mode"] == 0]
    df_maj_out = df_major
    df_min_out = df_minor

    df_maj_out["DJ Key"] = df_major["Key"].map(dict_keymap_maj)
    df_min_out["DJ Key"] = df_minor["Key"].map(dict_keymap_min)

    dfOut = pd.concat([df_maj_out,df_min_out],sort=False)
    return dfOut

# Sort df in the following manner. Group by bpm
def djSort(df_in,tempoRange,keyRange):
    df_tempoSort = getTracksWithTempo(df_in,tempoRange)

    # These values are under the assumption that the spotify notation is in "Major" keys. Looks like it doesn't matter immediately, can check though.
    # mapping keys to the way traktor sorts keys, so that close values are easier to mix into.

#    df_tempoSort = djMapKey(df_tempoSort)    
    tempo_vals = df_tempoSort["Tempo"]
    tempo_vals = np.floor(tempo_vals)
    tempo_vals_unique = np.unique(tempo_vals)

    df_out = pd.DataFrame()
    for t_val in tempo_vals_unique:
        ### TODO: low priority. Add additional major/minor sorting here.
        df_add = getTracksWithinRange(df_tempoSort[tempo_vals==t_val],"DJ Key",keyRange)
        df_out = pd.concat((df_out,df_add))
    return df_out

''' 
Playlist data analysis stuff. df_in
'''
def getTopGenres(sp,df_in):
    #this is a stub right now.

    artistURI = df_in["Artist URI"]
    uriFlat = [item for sublist in artistURI for item in sublist]

    searchRate = 30
    numSearches = len(uriFlat)

    uriSearch = uriFlat
    fullArtist = []
    midBreak = False
    while len(uriSearch) and (not midBreak): 
        if len(uriSearch) > searchRate:
            tmp = sp.artists(uriSearch[0:searchRate])
            fullArtist = fullArtist + (tmp["artists"])
            uriSearch = uriSearch[searchRate:]
               # print("here0")

        else:
            tmp = sp.artists(uriSearch[0:])
            fullArtist= fullArtist + (tmp["artists"])
            midBreak = True

    genresRet = [x["genres"] for x in fullArtist]
    genresFlat = [item for sublist in genresRet for item in sublist]
    genres_df = pd.DataFrame(data=genresFlat, columns = ["genres"])
    genreHist = genres_df["genres"].value_counts()
    #genreNames = genreHist.rows.values[0:5]
    return ( genreHist.index.tolist(),genreHist.values)

   # uri_list = [','.join(x) for x in ]
    #artistObjs = sp.Artists(df_in["Artist URI"])    


#get tracks within certain range of values 
def getTracksWithinRange(df_in,category,catRange):
    df_tmp = df_in[df_in[category] >= catRange[0]]
    df_out = df_tmp[df_tmp[category] <= catRange[1]]
    df_out = df_out.sort_values(by=[category],ascending = True)
    return df_out


# get tracks with set Tempo
def getTracksWithTempo(df_in,bpmRange,checkDouble = True):
    df_tmp = df_in[df_in["Tempo"] >= bpmRange[0]]
    df_out = df_tmp[df_tmp["Tempo"] <= bpmRange[1]]
    if checkDouble:
        df_tmp = df_in[df_in["Tempo"]>= bpmRange[0]*2]
        df_z2 = df_tmp[df_tmp["Tempo"] <= bpmRange[1]*2]

        col_tmp = df_z2["Tempo"]
        col_tmp /= 2
        df_z2["Tempo"] = col_tmp

        df_out = pd.concat((df_out,df_z2))

    df_out = df_out.sort_values(by=["Tempo"],ascending = True)
    return df_out


'''
## Playlist management
'''
# createPlaylist(sp, playlistName,objIn, incAnalysis): Create playlist with playlistName for the currently authorized user.
#    objIn can be either a list of track IDs or a dataframe with the unified structure this imports into. incAnalysis is only
#    a valid option if the object in is a dataframe, and includes some analysis in the playlist description.

def createPlaylist(sp,playlistName,objIn,incAnalysis = False):
    
    currUser = sp.me()
    userID = currUser["id"]
    now = datetime.now()
    dtString=now.strftime("%m/%d/%Y %H:%m:%S")

    if isinstance(objIn,pd.DataFrame):
        dfIn = True
        df = objIn
        analyzeAf = incAnalysis
    else:
        dfIn = False
        analyzeAf = False


    if analyzeAf:
        #Generate relevant means (Practically should just do the mean over the whole DF and get the specific thing but w/e)
        genresIn,genreCount = getTopGenres(sp,objIn)
        genresRep = genresIn[0:3]
        genresPrint = "Top Genres: "+ ", ".join(genresRep)+ " || "
        tempoMean =  df["Tempo"].mean(axis=0)
        danceMean =  df["Danceability"].mean(axis=0)
        energyMean =  df["Energy"].mean(axis=0)
        accousticMean =  df["Acousticness"].mean(axis=0)
        liveMean =  df["Liveness"].mean(axis=0)
        valenceMean =  df["Valence"].mean(axis=0)
        instrMean =  df["Instrumentalness"].mean(axis=0)
    
        str0 = "autogen playlist: "+ dtString +(" || Mean Tempo: %0.2f" %tempoMean)  
        str1 =  (" || Mean Danceability: %0.2f" %danceMean) 
        str2 =  (" || Mean Energy: %0.2f" %energyMean)  
        str3=  (" || Mean Accoustic: %0.2f" %accousticMean)   
        str4=   (" || Mean Liveness: %0.2f" %liveMean)  
        str5 =  (" || Mean Valence: %0.2f" %valenceMean)  
        str6 = (" || Mean Instrumentalness: %0.2f"%instrMean)
        strDescription = genresPrint + str0+str1+str2+str3+str4+str5 +str6   
    else: #Assuming for the moment else is a list of IDs
        strDescription = "Created "+ dtString
                    
    newPlay = sp.user_playlist_create(userID,playlistName,public=False,description=strDescription)
    
    playID = newPlay["id"]    
    midBreak= False    

    if dfIn:
        df_ids = df["Song URI"]
        while (not df_ids.empty) and (not midBreak): 
            if df_ids.size > 100:
                sp.playlist_add_items(playID, df_ids.iloc[0:100])
                df_ids = df_ids.iloc[100:]
            else:
                sp.playlist_add_items(playID, df_ids.iloc[0:])
                midBreak = True

    else: #Assuming list of ids, or names, or spotify URIs 
        idsProc = objIn
        midBreak= False    
        while len(idsProc) and (not midBreak): 
            if len(idsProc) > 100:
                sp.playlist_add_items(playID, idsProc[0:100])
                idsProc = idsProc[100:]
               # print("here0")

            else:
               # print(lenIdsProc)
                sp.playlist_add_items(playID, idsProc[0:])
                midBreak = True


# Note: Currently assuming list of ID strings as input for objin.
def addToPlaylist(sp,playlistName,objIn):
    plID = getPlaylistID(sp,playlistName)

    numRun = int(floor(len(objIn)/100))

    for elt in range(numRun):
        sp.playlist_add_items(plID,objIn[elt*numRun:elt*numRun+100])

    sp.playlist_add_items(plID,objIn[numRun*100:])

def compilePlaylists(sp,playlistSearch,playlistRemove,playlistTitle):
    dw_ids = getPlaylistIDs(sp,playlistSearch)
    dw_ids = list(filter(None,dw_ids))
    dw_ids = [elt for elt in dw_ids if elt!='37i9dQZEVXcScWD9gb8qCj']

    trackIds = []
    for playID in dw_ids:
        (tmp,)= getTracksFromPlaylist(sp,playID,False,False)
        trackIds = trackIds + tmp

    print("Num PL: "+ str(len(dw_ids)))
    print("Num Track IDs:" + str(len(trackIds)))

    # If you don't care about order then use a set instead, but I do - Max
    trackIdsUnique = list(dict.fromkeys(trackIds))
    print("Number of unique tracks: " + str(len(trackIdsUnique)))

    # Remove blacklisted tracks
    pl_id = getPlaylistID(sp,playlistRemove)
    (trackIds_rm,) = getTracksFromPlaylist(sp,pl_id,False,False)
    for idVal in trackIds_rm:
        try:
            trackIdsUnique.remove(idVal)
        except:
            pass

    indOut = removeSavedTracks(sp,trackIdsUnique)
    tracksOut = [trackIdsUnique[idx] for idx in indOut]
    print("Num tracks in playlist: "+str(len(tracksOut)))
    #### TODO: understand why this is losing some of the tracks.
    createPlaylist(sp,playlistTitle,tracksOut)


#samplePlaylists: from a playlist, generate nPlaylists randomly drawn playlists from it, and remove the songs
def samplePlaylists(sp, plName,nPlaylists,nSongsPerPlaylist,removeTracks=True):
    pl_id = getPlaylistID(sp,plName)
    (tmp1,) = getTracksFromPlaylist(sp,pl_id,False,False)

    nSample = min(nPlaylists*nSongsPerPlaylist, len(tmp1))
    if nSample >= nPlaylists:
        valsSample = random.sample(population=range(len(tmp1)),k=nSample)
        playlistLen = floor(nSample/nPlaylists)
        for idx in range(nPlaylists):
            idxUse = valsSample[idx*playlistLen:(idx+1)*playlistLen]
            tracksUse = [tmp1[idx2] for idx2 in idxUse]
            createPlaylist(sp,plName+" subsampling: "+ str(idx+1),tracksUse,False)
            if removeTracks:
                removeTracksFromPlaylist(sp,pl_id,tracksUse)
    elif nSample > 0:
        createPlaylist(sp,plName+" subsampling: ",tmp1,False)
        if removeTracks:
            removeTracksFromPlaylist(sp,pl_id,tmp1)
                

def cyclePlaylist(sp,playlistName,nDaysCycle,removeTracks=False,newPl = True):
    today=date.today() 
    pl_id = getPlaylistID(sp,playlistName)
    tr_ids,tr_times = getTracksFromPlaylist(sp,pl_id,ret_track_info = False,ret_af = False,ret_pl_info=True)
    timeFormatStr = "%Y-%m-%dT%H:%M:%SZ"
    tr_times_datetime = [datetime.strptime(elt,timeFormatStr) for elt in tr_times]

    dWeekAgo = today - timedelta(days=nDaysCycle)
    idsAdjust = []
    # def not pythonic but whatever at the moment.
    for (idx,elt) in enumerate(tr_times_datetime):
        if dWeekAgo > elt.date(): 
            idsAdjust += [tr_ids[idx]]

    date_str_add = datetime.strftime(today,"%B %Y")
    string_add = playlistName + ", " + date_str_add
    if idsAdjust: 
        if newPl:
            # create playlist\
            createPlaylist(sp,string_add,idsAdjust,False)
        else:
            addToPlaylist(sp,string_add,idsAdjust)

        if removeTracks:
            removeTracksFromPlaylist(sp,pl_id,idsAdjust)

        return idsAdjust
    else: 
        print("No tracks to remove.")
        return []

def getSimilarPlaylist(sp,plSearch,targetSampleSize,genSameSize=False,targetPopularity = 50,popRange=[0,100],tempoRange=[0,200]):
    usePopRange = True
    recIDs = []
    pl_id = getPlaylistID(sp,plSearch)
    trackDict,afDict = getTracksFromPlaylist(sp,pl_id,True,True)
    trackIDs  =  [item["id"] for item in trackDict if item["id"]]
    tracksIDs = random.shuffle(trackIDs)

    if genSameSize:
        nQuery = floor(len(trackIDs)/targetSampleSize)
    else:
        nQuery = floor(len(trackIDs)/5)

    recIDsUnique=[0]
    while len(recIDsUnique) < targetSampleSize:
        for idx in range(nQuery):
            if usePopRange:
                recRet = sp.recommendations(seed_tracks=trackIDs[idx*5:(idx+1)*5],limit=targetSampleSize,min_tempo=tempoRange[0],max_tempo = tempoRange[1],market="US",min_popularity=popRange[0],max_popularity=popRange[1])
            else:
                recRet = sp.recommendations(seed_tracks=trackIDs[idx*5:(idx+1)*5],limit=targetSampleSize,min_tempo=tempoRange[0],max_tempo = tempoRange[1],market="US",target_popularity=targetPopularity)
            recTracks= recRet["tracks"]
            recIDs = recIDs + [elt["id"] for elt in recTracks if ("US" in elt["available_markets"])]
            recIDsUnique = list(dict.fromkeys(recIDs))
            if len(recIDsUnique)> targetSampleSize:
                break

    ### TODO: get recTracks into recIDsUnique format, get sp.audio_features() of the ids to djsort similar playlists.
    createPlaylist(sp,"Similar to "+plSearch,recIDsUnique,incAnalysis = False)


# removeSavedTracks(sp,trackIDs): Given a list of track IDs, return the indices of tracks that haven't been saved into the users library yet.
def removeSavedTracks(sp,trackIDs):
    divVal = 30 #arbitrary, must be 50 or less.
    numelUnique = len(trackIDs)
    numCalls = int(np.ceil(numelUnique/divVal))
    # Eventually functionize this.
    tmp = []
    songsLiked = []

    for ind in range(numCalls):
        if ind < (numCalls-1):
            tmp = trackIDs[(0+ind*divVal):(divVal+ind*divVal)]
            # print("BREAKBREAK")#
        else:
            tmp = trackIDs[(0+ind*divVal):]

        songsLiked = songsLiked + sp.current_user_saved_tracks_contains(tracks=tmp)

    songsUnliked = [not x for x in songsLiked]
    indOut = np.where(songsUnliked)
    return indOut[0]

def removeTracksFromPlaylist(sp,plID,trackIDs):
    nRemove = int(np.ceil(len(trackIDs)/100))
    nTracks = len(trackIDs)
    for elt in range(nRemove):
        nTracksRemove = min(100,nTracks)
#        print(nTracksRemove)
        # print(trackIDs[elt*100:elt*100+nTracksRemove])
        sp.playlist_remove_all_occurrences_of_items(plID,trackIDs[elt*100:elt*100+nTracksRemove])
        nTracks -= nTracksRemove


'''
Dataframe/spotify object interactions.
'''
### TODO: Give option to return artist list.
# tracksToDF(tracks,af): convert the tracks and af objects spotipy produces to a unified dataframe.
def tracksToDF(tracks,af,artistList = False):
    # Currently, putting off the most annoying parts (indexing to get the artist name)
    
    artistObjs = [x["album"]["artists"] for x in tracks]
    artistName = []
    artistURI = []
    album = []
    genresObjs = 0
    for idx,elt in enumerate(artistObjs):
        artistName.append( [x["name"] for x in elt])
        artistURI.append([x["uri"] for x in elt])

    if artistList:
        artistName = [','.join(x) for x in artistName]
        artistURI =  [','.join(x) for x in artistURI]

    trackDict = {
        "Title": [x["name"] for x in tracks],
        "Track ID":[x["id"] for x in tracks],
        "Song URI": [x["uri"] for x in tracks],
        "Artist":artistName,
        "Artist URI": artistURI,
        "Album Name":  [x["album"]["name"] for x in tracks],
        "Duration_ms":[x["duration_ms"] for x in tracks],
        "Acousticness" : [x["acousticness"] for x in af],
        "Danceability":[x["danceability"] for x in af],
        "Energy":[x["energy"] for x in af],
        "Instrumentalness":[x["instrumentalness"] for x in af],
        "Key":[x["key"] for x in af],
        "Mode":[x["mode"] for x in af],
        "Liveness":[x["liveness"] for x in af],
        "Loudness":[x["loudness"] for x in af],
        "Speechiness":[x["speechiness"] for x in af],
        "Tempo":[x["tempo"] for x in af],
        "TimeSig":[x["time_signature"] for x in af],
        "Valence":[x["valence"] for x in af],
        
    }
    retDF = pd.DataFrame.from_dict(trackDict)
    retDF = djMapKey(retDF) 
    return retDF


'''
Exporting to CSV
'''
def saveTrackDF(df,filepath):
    dfTmp = df
    if isinstance(df["Artist"][0],list):
        # Note: Here there may be a smarter delimiter between artists and artist URIS, 
        dfTmp["Artist"] = dfTmp["Artist"].apply(lambda x:",".join(x))
        dfTmp["Artist URI"] = dfTmp["Artist URI"].apply(lambda x:",".join(x))
    dfTmp.to_csv(filepath)

# Exporting playlist info to CSV
def savePlaylistToCSV(sp,plName,filepath,sortTempo=False):
    plID = getPlaylistID(sp,plName)
    tracksSave,audioFeatures = getTracksFromPlaylist(sp,plID)
    df_save = tracksToDF(tracksSave,audioFeatures)
    if sortTempo:
        df_save = getTracksWithTempo(df_save,[0, 300],False)

    saveTrackDF(df_save,filepath)
    

