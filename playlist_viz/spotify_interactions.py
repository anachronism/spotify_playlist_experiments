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

def createPlaylist(playlistName,df):
        
    CLIENT_ID = secretsLocal.clientID()
    CLIENT_SECRET = secretsLocal.clientSecret()
    REDIRECT_URI = "http://localhost:8080" # NOTE:Must add this to your spotify app suitable links. 
    scope="playlist-modify-private"
    
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,client_id=CLIENT_ID,client_secret=CLIENT_SECRET,redirect_uri=REDIRECT_URI))
    
    currUser = sp.me()
    userID = currUser["id"]
    newPlay = sp.user_playlist_create(userID,playlistName,public=False,description="autogen playlist")
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
    

