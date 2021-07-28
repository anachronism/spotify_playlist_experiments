import numpy as np 
import pandas as pd
import utils 
from crate_compile import crateCompile
from song_corpus_analysis import analyseSongCorpus
import spotify_interactions as si

import datetime
today=datetime.date.today() 
recentGenDW = today-datetime.timedelta(days=today.weekday())
dwDate = recentGenDW.strftime("%m/%d/%Y")

edgeDate = "06/25/2021"
pulseDate = "07/15/2021"

plNames = [
        ["Remove from combined DW","Combined DW for the Week of "+dwDate],
        ["RR Remove","RR Listen through"],  
        ["downselect_downselect_remove","downselect_downselect_listen"], 
        ["Edge Playlist Clear","Combined Edge Playlists "+edgeDate],
        ["Pulse Playlist Clear", "Combined Pulse Playlists "+pulseDate]]


sp = si.initSpotipy("playlist-modify-private")

for elt in plNames:
    plName1 = elt[0]
    plName2 = elt[1]
    pl_id = si.getPlaylistID(sp,plName1)
    trackDict,__ = si.getTracksFromPlaylist(sp,pl_id,True,True)
    trackIDs  =  [item["id"] for item in trackDict if item["id"]]


    pl_remove = si.getPlaylistID(sp,plName2)
    print(elt)
    si.removeTracksFromPlaylist(sp,pl_remove,trackIDs)
    si.removeTracksFromPlaylist(sp,pl_id,trackIDs)
