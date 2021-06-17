import spotify_interactions as si 
from datetime import datetime

now = datetime.now()
dtString=now.strftime("%m/%d/%Y")
playlistTitle = "Combined DW for the Week of " + dtString

playlistSearch = "Discover Weekly"

sp = si.initSpotipy("playlist-read-private playlist-modify-private user-library-read")# 


dw_ids = si.getPlaylistIDs(sp,playlistSearch)
dw_ids = list(filter(None,dw_ids))
dw_ids = [elt for elt in dw_ids if elt!='37i9dQZEVXcScWD9gb8qCj']

print(dw_ids)
trackIds = []
for playID in dw_ids:
	tmp= si.getTracksFromPlaylist(sp,playID,False,False)
	trackIds = trackIds + tmp

print("Num DW: "+ str(len(dw_ids)))
print("Num Track IDs:" + str(len(trackIds)))

# If you don't care about order then use a set instead, but I do - Max
trackIdsUnique = list(dict.fromkeys(trackIds))
print("Number of unique tracks: " + str(len(trackIdsUnique)))


indOut = si.removeSavedTracks(sp,trackIdsUnique)


tracksOut = [trackIdsUnique[idx] for idx in indOut]
print("Num tracks in playlist: "+str(len(tracksOut)))
#### TODO: understand why this is losing some of the tracks.
si.createPlaylist(sp,playlistTitle,tracksOut)
