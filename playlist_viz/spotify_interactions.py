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

def createPlaylist(playlistName,df):
        
    CLIENT_ID = secretsLocal.clientID()
    CLIENT_SECRET = secretsLocal.clientSecret()
    REDIRECT_URI = "http://localhost:8080" # NOTE:Must add this to your spotify app suitable links. 
    scope="playlist-modify-private"
    
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,client_id=CLIENT_ID,client_secret=CLIENT_SECRET,redirect_uri=REDIRECT_URI))
    
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
    

