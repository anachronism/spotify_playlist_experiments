import spotify_interactions as si 
from datetime import datetime

now = datetime.now()
dtString=now.strftime("%m/%d/%Y")
playlistTitle = "Combined Edge Playlists "+ dtString

playlistSearch = "The Edge of"
playlistRemove = "Discovery Avoid"

sp = si.initSpotipy("playlist-read-private playlist-modify-private user-library-read")# 

si.compilePlaylists(sp,playlistSearch,playlistRemove,playlistTitle)

