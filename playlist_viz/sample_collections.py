import spotify_interactions as si 
from datetime import datetime
import pandas as pd
import random 
from math import floor
# playlists=["Combined DW for the Week of 07/12/2021"]
playlists=[\
            "downselect_downselect_listen", \
            "Combined Edge Playlists 06/25/2021", \
            "Combined DW for the Week of 07/12/2021", \
            "Combined Pulse Playlists 07/15/2021"
            ]
nPlaylists = 2
nSongsPerPlaylist = 30


sp = si.initSpotipy("playlist-read-private playlist-modify-private user-library-read")# 

for elt in playlists:
    pl_id = si.getPlaylistID(sp,elt)
    tmp1 = si.getTracksFromPlaylist(sp,pl_id,False,False)

    nSample = min(nPlaylists*nSongsPerPlaylist, len(tmp1))
    if nSample > nPlaylists:
        valsSample = random.sample(population=range(len(tmp1)),k=nSample)
        print(nSample)
        playlistLen = floor(nSample/nPlaylists)
        for idx in range(nPlaylists):
            idxUse = valsSample[idx*playlistLen:(idx+1)*playlistLen]
            tracksUse = [tmp1[idx2] for idx2 in idxUse]
            si.createPlaylist(sp,elt+" subsampling: "+ str(idx+1),tracksUse,False)
            si.removeTracksFromPlaylist(sp,pl_id,tracksUse)
    
