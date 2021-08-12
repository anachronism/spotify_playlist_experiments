import spotify_interactions as si 
from datetime import datetime
import pandas as pd
import random 
from math import floor

import datetime
today=datetime.date.today() 
recentGenDW = today-datetime.timedelta(days=today.weekday())
dwDate = recentGenDW.strftime("%m/%d/%Y")
edgeDate = "07/30/2021"
pulseDate = "07/15/2021"

# playlists=["RR Listen through"]
playlists=[\
            "downselect_downselect_listen", \
            "Combined Edge Playlists "+edgeDate, \
            "Combined Pulse Playlists "+pulseDate,
            "Combined DW for the Week of "+dwDate, \
            "RR Listen through"
            ]

nPlaylists =2
nSongsPerPlaylist = 15
FLAG_RUN = True


if FLAG_RUN:
    sp = si.initSpotipy("playlist-read-private playlist-modify-private user-library-read")# 

    for elt in playlists:
        si.samplePlaylists(sp,elt,nPlaylists,nSongsPerPlaylist)
