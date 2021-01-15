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


## ID acquisitions
# getPlaylistID(sp,strName): With sp handle, get the first playlist that has a title that directly matches the provided string.
def getPlaylistID(sp,strName):    
    # search, must match.
    currUser = sp.me()
    userID = currUser["id"]

    foundPlaylist = False
    offset = 0
    currVal = sp.current_user_playlists(limit=50, offset=offset)
        
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

        tmp = [item for item in plList if (strName in item["name"]) ]  
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
        
        newIDs = [item["id"]for item in tracksNew]
        trackIds = trackIds + newIDs

        if ret_af:
            audioFeatures = audioFeatures + sp.audio_features(newIDs)
        nextUp = plHandle["next"]

    if ret_track_info:
        trackOut = tracksSave
    else:
        trackOut = trackIds#trackURIs
    if ret_af:
        return trackOut,afOut
    else:
        return trackOut


''' 
Playlist data analysis stuff
'''
def getTopGenres(df_in):
    #this is a stub right now.    
    return []


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
        strDescription = str0+str1+str2+str3+str4+str5 +str6   
    else: #Assuming for the moment else is a list of IDs
        strDescription = "Created "+ dtString
                    
    newPlay = sp.user_playlist_create(userID,playlistName,public=False,description=strDescription)
    
    playID = newPlay["id"]    
    midBreak= False    

    if dfIn:
        df_ids = df["Track URI"]
        while (not df_ids.empty) and (not midBreak): 
            if df_ids.size > 100:
                sp.playlist_add_items(playID, df_ids.iloc[0:99])
                df_ids = df_ids.iloc[100:]
            else:
                sp.playlist_add_items(playID, df_ids.iloc[0:])
                midBreak = True

    else: #Assuming list of ids, or names, or spotify URIs 
        idsProc = objIn
        midBreak= False    
        while len(idsProc) and (not midBreak): 
            if len(idsProc) > 100:
                sp.playlist_add_items(playID, idsProc[0:99])
                idsProc = idsProc[100:]
               # print("here0")

            else:
                sp.playlist_add_items(playID, idsProc[0:])
                midBreak = True

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


'''
Dataframe/spotify object interactions.
'''
# tracksToDF(tracks,af): convert the tracks and af objects spotipy produces to a unified dataframe.
def tracksToDF(tracks,af):
    # Currently, putting off the most annoying parts (indexing to get the artist name)
    
    artistObjs = [x["album"]["artists"] for x in tracks]
    artistName = []
    artistURI = []
    for idx,elt in enumerate(artistObjs):
        artistName.append( [x["name"] for x in elt])
        artistURI.append([x["uri"] for x in elt])

    trackDict = {
        "Album Name":  [x["album"]["name"] for x in tracks],
        "Title": [x["name"] for x in tracks],
        "Song URI": [x["uri"] for x in tracks],
        "Artist":artistName,
        "Artist URI": artistURI,
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
    

