import numpy as np 
import pandas as pd
import utils 
from crate_compile import crateCompile
from song_corpus_analysis import analyseSongCorpus
import spotify_interactions as si

# plName1 = "RR Remove"
# plName2 = "RR Listen through"

# plName1 = "Remove from combined DW"
# plName2 = "Combined DW for the Week of 06/15/2021"

# plName1 = "downselect_downselect_remove"
# plName2 = "downselect_downselect_listen"


plNames = [
        ["Remove from combined DW","Combined DW for the Week of 07/12/2021"],
        ["RR Remove","RR Listen through"],  
        ["downselect_downselect_remove","downselect_downselect_listen"], 
        ["Edge Playlist Clear","Combined Edge Playlists"],
        ["Pulse Playlist Clear", "Combined Pulse Playlists 07/15/2021"]]


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
