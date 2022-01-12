Max's Spotify Projects:
=========================
As of present, Playlist Viz folder has everything I've done on this. Next steps are just random feature adds, as well as trying to replace the embed-clustering workflow with an autoencoder or variational auto encoder. 
global_daily_script.py contains the workflow that I'm running regularly. I broke song_corpus_viz.py at some point (oops) but that contains some of the jank cluster visualization stuff I had done.

Playlist Viz: looking into dividing crate playlists into smaller playlists. Relatively simple, based off of some dimensionality reduction and some clustering/partitioning. Viz is currently simple but can experiment with it. Should try to pull together a few crate playlists and see what comes of it.
https://stackoverflow.com/questions/5452576/k-means-algorithm-variation-with-equal-cluster-size

Playlist continuation: Trying to make playlists like some of the ordered playlists I included, from liked songs csv or combined crates. Needs some sort of playlist characterization or genre characterization or something along those lines. 

