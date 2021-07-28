import spotify_interactions as si 
from datetime import datetime
import pandas as pd
import random 
from math import floor

import datetime
today=datetime.date.today() 
recentGenDW = today-datetime.timedelta(days=today.weekday())
dwDate = recentGenDW.strftime("%m/%d/%Y")
edgeDate = "06/25/2021"
pulseDate = "07/15/2021"

# playlists=["Combined DW for the Week of 07/26/2021"]
playlists=[\
            "downselect_downselect_listen", \
            "Combined Edge Playlists "+edgeDate, \
            "Combined Pulse Playlists "+pulseDate,
            "Combined DW for the Week of "+dwDate, \
            "RR Listen through"
            ]

nPlaylists =4
nSongsPerPlaylist = 15


sp = si.initSpotipy("playlist-read-private playlist-modify-private user-library-read")# 

for elt in playlists:
    si.samplePlaylists(sp,elt,nPlaylists,nSongsPerPlaylist)

    # pl_id = si.getPlaylistID(sp,elt)
    # tmp1 = si.getTracksFromPlaylist(sp,pl_id,False,False)

    # nSample = min(nPlaylists*nSongsPerPlaylist, len(tmp1))
    # if nSample >= nPlaylists:
    #     valsSample = random.sample(population=range(len(tmp1)),k=nSample)
    #     print(nSample)
    #     playlistLen = floor(nSample/nPlaylists)
    #     for idx in range(nPlaylists):
    #         idxUse = valsSample[idx*playlistLen:(idx+1)*playlistLen]
    #         tracksUse = [tmp1[idx2] for idx2 in idxUse]
    #         si.createPlaylist(sp,elt+" subsampling: "+ str(idx+1),tracksUse,False)
    #         si.removeTracksFromPlaylist(sp,pl_id,tracksUse)
