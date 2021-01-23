# Visualization improvements
## Cluster size analysis
* Top level statistics at the top: Playlist sizes
* Get closest cluster to currently active on second pane
* Pull largest clusters

## Better tool use
* Search corpus if song is in there.
* Get number of songs liked on playlist, return for discover weeklies
    * Cull playlists with most liked at beginning, move up playlists with most liked at end (Maybe keep new likes list?). 
* Refactor to make it easier to process the clusters after calculating
    * Size, energy, valence etc
* List, sorted by various parameters, selectable.

## Plot efficiency
* Make each cluster a different trace so that it might be easier to update the figure.

# Algorithm improvements
* Look into autoencoders for embedding.
    * Pull in own playlists to look at how they look in the embedding.

 