# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 19:09:45 2021

@author: Max

"""
# Shows the top tracks for a user

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import secretsLocal # NOTE: Must create this file yourself. Make functions that return the id and secret.
import pandas as pd 
from datetime import datetime

def initSpotipy():
    CLIENT_ID = secretsLocal.clientID()
    CLIENT_SECRET = secretsLocal.clientSecret()
    REDIRECT_URI = "http://localhost:8080" # NOTE:Must add this to your spotify app suitable links. 
    scope="playlist-modify-private"
    
    
    return spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,client_id=CLIENT_ID,client_secret=CLIENT_SECRET,redirect_uri=REDIRECT_URI))


def createPlaylist(playlistName,df):
        
    
    sp = initSpotipy()

    #Generate relevant means (Practically should just do the mean over the whole DF and get the specific thing but w/e)
    tempoMean =  df["Tempo"].mean(axis=0)
    danceMean =  df["Danceability"].mean(axis=0)
    energyMean =  df["Energy"].mean(axis=0)
    accousticMean =  df["Acousticness"].mean(axis=0)
    liveMean =  df["Liveness"].mean(axis=0)
    valenceMean =  df["Valence"].mean(axis=0)
    instrMean =  df["Instrumentalness"].mean(axis=0)
    
    currUser = sp.me()
    userID = currUser["id"]
    now = datetime.now()
    dtString=now.strftime("%m/%d/%Y %H:%m:%S")
    str0 = "autogen playlist: "+ dtString +(" || Mean Tempo: %0.2f" %tempoMean)  
    str1 =  (" || Mean Danceability: %0.2f" %danceMean) 
    str2 =  (" || Mean Energy: %0.2f" %energyMean)  
    str3=  (" || Mean Accoustic: %0.2f" %accousticMean)   
    str4=   (" || Mean Liveness: %0.2f" %liveMean)  
    str5 =  (" || Mean Valence: %0.2f" %valenceMean)  
    str6 = (" || Mean Instrumentalness: %0.2f"%instrMean)

    strDescription = str0+str1+str2+str3+str4+str5 +str6   
                    
    newPlay = sp.user_playlist_create(userID,playlistName,public=False,description=strDescription)
    playID = newPlay["id"]
    
    df_ids = df["Track URI"]
    midBreak= False
    
    while (not df_ids.empty) and (not midBreak): 
        if df_ids.size > 100:
            sp.playlist_add_items(playID, df_ids.iloc[0:99])
            df_ids = df_ids.iloc[100:]
        else:
            sp.playlist_add_items(playID, df_ids.iloc[0:])
            midBreak = True
    
def getTopGenres(df_in):
    #this is a stub right now.
    
    return []

def getPlaylistID(sp,strName):    
    
    currUser = sp.me()
    userID = currUser["id"]

    foundPlaylist = False
    offset = 0
   
    while not foundPlaylist:
        currVal = sp.current_user_playlists(limit=50, offset=offset)
        plList = currVal["items"]
        tmp = next((item for item in plList if item["name"] == strName),None)
        if not (tmp is None):
            foundPlaylist = True
            return tmp["id"]
        else:
            offset = offset +plList["limit"]


def getTracksFromPlaylist(sp,plName):
    idUse = getPlaylistID(sp,plName)
    offset = 0
    plHandle = sp.playlist_items(idUse,offset = offset)
    nTracks = plHandle["total"]
    trackIds = []
    audioFeatures = []
    audioAnalysis = []
    tracksSave = []

    while not( plHandle["next"] is None):
        # save tracks.
        plHandle = sp.playlist_items(idUse,offset = offset) 
        tracksNew = [item["track"] for item in plHandle["items"]]
        tracksSave = tracksSave + tracksNew
        newIDs = [item["id"]for item in tracksNew]


        trackIds = trackIds + newIDs
        audioFeatures = audioFeatures + sp.audio_features(newIDs)
        # for idx in newIDs:
        #     audioAnalysis.append(sp.audio_analysis( idx))
        #     print(idx)

        offset = offset + plHandle["limit"]
    return (tracksSave,audioFeatures)

def tracksToDF(tracks,af):
    # Currently, putting off the most annoying parts (indexing to get the artist name)
    artistObjs = [x["album"]["artists"] for x in tracks]

    trackDict = {
        "Album Name":  [x["album"]["name"] for x in tracks],
        "Title": [x["name"] for x in tracks],
        "Song URI": [x["uri"] for x in tracks],
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

def saveTrackDF(df,filepath):
    df.to_csv(filepath)

def savePlaylistToCSV(plName,filepath):
    sp = initSpotipy()
    tracksSave,audioFeatures = getTracksFromPlaylist(sp,plName)
    df_save = tracksToDF(tracksSave,audioFeatures)
    saveTrackDF(df_save,filepath)
    


