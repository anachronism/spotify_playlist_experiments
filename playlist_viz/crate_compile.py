import spotify_interactions as si 
from datetime import datetime
import pandas as pd

model_folder = "pkl_vals"
fid_inputPkl = "/".join((model_folder,"crates_compiled.pkl"))

playlistSearch = "/* CRATE"
sp = si.initSpotipy("playlist-read-private playlist-modify-private user-library-read")# 


pl_ids = si.getPlaylistIDs(sp,playlistSearch)
trackDict = []
analysisDict = []
for playID in pl_ids:
    print(playID)
    tmp1,tmp2 = si.getTracksFromPlaylist(sp,playID,True,True)
    if tmp2 is None:
        tmp1,tmp2 = si.getTracksFromPlaylist(sp,playID,True,True)

    trackDict = trackDict + tmp1
    analysisDict = analysisDict + tmp2 

playlistSearch2 = "The Downselect"
pl_ids2 = si.getPlaylistIDs(sp,playlistSearch2)
for playID in pl_ids2:
    print(playID)
    tmp1,tmp2 = si.getTracksFromPlaylist(sp,playID,True,True)

    if tmp2 is None:
        tmp1,tmp2 = si.getTracksFromPlaylist(sp,playID,True,True)

    trackDict = trackDict + tmp1
    analysisDict = analysisDict + tmp2 

print("Num Track IDs:" + str(len(trackDict)))

idxUse = [idx for idx,val in enumerate(analysisDict) if not (val is None)]
trackDictUse = [trackDict[idx] for idx in idxUse]
analysisDictUse = [analysisDict[idx]for idx in idxUse]

# If you don't care about order then use a set instead, but I do - Max
trackDF = si.tracksToDF(trackDictUse,analysisDictUse,False)
trackDF = trackDF.drop_duplicates(subset=["Song URI"])
print("Number of unique tracks: " + str(len(trackDF.index)))
trackDF.to_pickle(fid_inputPkl)

#indOut = si.removeSavedTracks(sp,trackIdsUnique)

#tracksOut = [trackIdsUnique[idx] for idx in indOut]
#print("Num tracks in playlist: "+str(len(tracksOut)))
#### TODO: understand why this is losing some of the tracks.
#si.createPlaylist(sp,playlistTitle,tracksOut)