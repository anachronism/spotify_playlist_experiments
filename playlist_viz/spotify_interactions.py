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
from datetime import datetime

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
def searchPlaylistForTempo(sp,plName,bpmRange,checkDouble=True):
    pl_id = getPlaylistID(sp,plName)
    if pl_id == -1:
        print("PLAYLIST NOT FOUND")  
        return -1
    else:  
        tracks_pl,analysis_pl = getTracksFromPlaylist(sp,pl_id,True,True)
        print(bpmRange)
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
#        print(plList[0].keys())

        tmp = [item for item in plList if (strName.lower() in item["name"].lower()) ]  
        for elt in tmp:
            idsRet.append(elt["id"])

        offset = offset +currVal["limit"]

    return idsRet

# getTracksFromPlaylist(sp,plID,ret_track_info,ret_af):
# With sp handle and playlist ID, return list with info. if ret_track_info is True, it will return the whole song structure,
# otherwise it returns a list of track IDs. If ret_af is True it also returns the audio-features object for each track.
def getTracksFromPlaylist(sp,plID,ret_track_info = True,ret_af = True):
    offset = 0
    plHandle = sp.playlist_items(plID,offset = offset)
    nTracks = plHandle["total"]
    trackIds = []
    #trackURIs = []
    audioFeatures = []
    audioAnalysis = []
    tracksSave = []
    ret_track_info = ret_track_info
    ret_af = ret_af
    nextUp = 1
    while not (nextUp is None):
        if nextUp != 1:
            offset = offset + plHandle["limit"]
        # save tracks.
        plHandle = sp.playlist_items(plID,offset = offset) 
        tracksNew = [item["track"] for item in plHandle["items"]]
        tracksSave = tracksSave + tracksNew

        tracksNew = list(filter(None,tracksNew))
        newIDs = [item["id"]for item in tracksNew if item["id"]]
        trackIds = trackIds + newIDs

        if ret_af:
            audioFeatures = audioFeatures + sp.audio_features(newIDs)
        nextUp = plHandle["next"]

    if ret_track_info:
        trackOut = tracksSave
    else:
        trackOut = trackIds#trackURIs
    if ret_af:
        return trackOut,audioFeatures
    else:
        return trackOut


# Sort df in the following manner. Group by bpm
def djSort(df_in,tempoRange,keyRange):
    df_tempoSort = getTracksWithTempo(df_in,tempoRange)

    # These values are under the assumption that the spotify notation is in "Major" keys. Looks like it doesn't matter immediately, can check though.
    # mapping keys to the way traktor sorts keys, so that close values are easier to mix into.
    dict_keymap = {
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
    df_tempoSort["DJ Key"] = df_tempoSort["Key"].map(dict_keymap) 
    
    tempo_vals = df_tempoSort["Tempo"]
    tempo_vals = np.floor(tempo_vals)
    tempo_vals_unique = np.unique(tempo_vals)

    df_out = pd.DataFrame()
    for t_val in tempo_vals_unique:
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
                print(len(idsProc[0:100]))
                sp.playlist_add_items(playID, idsProc[0:100])
                idsProc = idsProc[100:]
               # print("here0")

            else:
               # print(lenIdsProc)
                sp.playlist_add_items(playID, idsProc[0:])
                midBreak = True


def compilePlaylists(sp,playlistSearch,playlistRemove,playlistTitle):
    dw_ids = getPlaylistIDs(sp,playlistSearch)
    dw_ids = list(filter(None,dw_ids))
    dw_ids = [elt for elt in dw_ids if elt!='37i9dQZEVXcScWD9gb8qCj']

    print(dw_ids)
    trackIds = []
    for playID in dw_ids:
        tmp= getTracksFromPlaylist(sp,playID,False,False)
        trackIds = trackIds + tmp

    print("Num PL: "+ str(len(dw_ids)))
    print("Num Track IDs:" + str(len(trackIds)))

    # If you don't care about order then use a set instead, but I do - Max
    trackIdsUnique = list(dict.fromkeys(trackIds))
    print("Number of unique tracks: " + str(len(trackIdsUnique)))

    # Remove blacklisted tracks
    pl_id = getPlaylistID(sp,playlistRemove)
    trackIds_rm = getTracksFromPlaylist(sp,pl_id,False,False)
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
#        print(trackIDs[elt*100:elt*100+nTracksRemove])
        print(trackIDs[elt*100+nTracksRemove-1])
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
        "Liveness":[x["key"] for x in af],
        "Loudness":[x["loudness"] for x in af],
        "Speechiness":[x["speechiness"] for x in af],
        "Tempo":[x["tempo"] for x in af],
        "TimeSig":[x["time_signature"] for x in af],
        "Valence":[x["valence"] for x in af],
        
    }
    return pd.DataFrame.from_dict(trackDict)


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
def savePlaylistToCSV(sp,plName,filepath):
    plID = getPlaylistID(plName)
    tracksSave,audioFeatures = getTracksFromPlaylist(sp,plID)
    df_save = tracksToDF(tracksSave,audioFeatures)
    saveTrackDF(df_save,filepath)
    

