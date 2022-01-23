import spotify_interactions as si
from datetime import datetime
import pandas as pd

def crateCompile(fid_in="pkl_vals/crates_compiled.pkl",searchIDs=["/* ","The Downselect"]):

    fid_inputPkl = fid_in
    sp = si.initSpotipy("playlist-read-private playlist-modify-private user-library-read")#

    trackDict = []
    analysisDict = []

    ## TODO: additional playlist age filter for drawing playlists.
    for playlistSearch in searchIDs:
        pl_ids = si.getPlaylistIDs(sp,playlistSearch)
        print(pl_ids)
        for playID in pl_ids:
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
