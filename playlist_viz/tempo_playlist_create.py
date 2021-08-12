import numpy as np 
import pandas as pd
import spotify_interactions as si 


sp = si.initSpotipy("playlist-read-private playlist-modify-private user-library-read")# 
tempo_range = [130,135]#[108,110]
key_range = [1,12] #12 total options.

runMode = 1

if runMode == 0:
    ## Search through already compiled crates
    crate_type = "downsel"
    #crate_type = "pulse_of"
    playlist_title = crate_type + " Tracks within "+str(tempo_range[0])+ " and " + str(tempo_range[1]) + " BPM " + str(key_range[0]) + " to "+ str(key_range[1])

    model_folder = "pkl_vals"
    fid_in = "/".join((model_folder,crate_type+"_compiled.pkl"))
    df_pool = pd.read_pickle(fid_in)

    df_out = si.djSort(df_pool,tempo_range,key_range)
#    df_out = si.getTracksWithTempo(df_pool,tempo_range)
    si.createPlaylist(sp,playlist_title,df_out)

elif runMode == 1:
    ## search through specific playlist
    pl_name = "The Downselect, July 2021 Weeks 1-2"#"The Downselect, 2021"#"Combined Pulse Playlists 07/15/2021"
    playlist_title = pl_name + ", From " + str(tempo_range[0]) + " to " + str(tempo_range[1]) + " BPM, Keys " + str(key_range[0]) + " to "+ str(key_range[1])
    df_out = si.searchPlaylistForTempo(sp,pl_name,tempo_range)
    df_out = si.djSort(df_out,tempo_range,key_range)
    ## Search through already compiled crates
    si.createPlaylist(sp,playlist_title,df_out)
