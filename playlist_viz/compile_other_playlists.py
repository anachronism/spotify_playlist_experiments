import spotify_interactions as si 

playlistOutput = "Combined Crates"
playlistSearch = "Kissaten Radio"

sp = si.initSpotipy("playlist-read-private playlist-modify-private user-library-read")# 

## TODO: figure out good way to have playlist names, might need to add a function to spotify_interactions to search a list of playlists.
## 		Currently, script either returns one playlist with the name, or multiple playlists that share a string in the title.  
##		Alternatively, you can throw the getPlaylistID call in a for loop and do it the same way I do get tracks, but I don't think that's efficient.
##		Two loops could be combined, but again, don't think thats necessary.

## TODO: You could make a jank UI to make getting playlist names easier.

# Get playlist IDs
pl_ids = [si.getPlaylistID(sp,playlistSearch)]
pl_ids = list(filter(None,pl_ids))
pl_ids = [elt for elt in pl_ids if elt!='37i9dQZEVXcScWD9gb8qCj'] # This was just my DW hardcode playlist ignore. 
print(pl_ids)

# Get tracks from playlist
trackIds = []
for playID in pl_ids:
	tmp= si.getTracksFromPlaylist(sp,playID,False,False)
	trackIds = trackIds + tmp

## TODO: Possibility is to dedup songs that have different IDs but matching artists and titles. Spotify's artist structure makes it kind of 
##			annoying but not impossible to do this.

# Get unique tracks by ID
trackIdsUnique = list(dict.fromkeys(trackIds))
print("Number of unique tracks: " + str(len(trackIdsUnique)))

# Remove tracks already in library.
indOut = si.removeSavedTracks(sp,trackIdsUnique) # This step is not strictly necessary, and doesn't seem to work all the time.
tracksOut = [trackIdsUnique[idx] for idx in indOut]

## TODO: You could make it so it adds to an existing playlist instead of creating a new one, but I don't have the spotipy API hooks in place to do that yet. 
# Write playlist out.
si.createPlaylist(sp,playlistTitle,tracksOut)

